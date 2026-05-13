#!/usr/bin/env python3
"""
Detect Source of Truth from code.

This script discovers current codebase facts and can regenerate SOURCE_OF_TRUTH.yaml.
Primary focus is MCP tool surface integrity, including tools/list vs tools/call parity.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

import yaml


project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_lucid_mcp_content() -> str:
    mcp_file = project_root / "lucid_mcp_server.py"
    if not mcp_file.exists():
        raise FileNotFoundError("lucid_mcp_server.py not found")
    return mcp_file.read_text(encoding="utf-8", errors="ignore")


def _extract_bracket_block(content: str, assignment_token: str) -> str:
    """
    Extract the first balanced [] block after assignment_token.
    This is robust against nested arrays in schemas.
    """
    token_pos = content.find(assignment_token)
    if token_pos == -1:
        return ""

    open_pos = content.find("[", token_pos)
    if open_pos == -1:
        return ""

    depth = 0
    for i in range(open_pos, len(content)):
        ch = content[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return content[open_pos : i + 1]
    return ""


def _extract_handle_tools_call_block(content: str) -> str:
    start = content.find("def handle_tools_call(")
    if start == -1:
        return ""
    end = content.find("\n    def ", start + 1)
    if end == -1:
        end = len(content)
    return content[start:end]


def _extract_header_docstring(content: str) -> str:
    match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    return match.group(1) if match else ""


def _extract_header_categories(docstring: str) -> Dict[str, int]:
    """
    Parse category lines from the top module docstring, e.g.
    Core AIM-OS (6): store_memory, ...
    """
    categories: Dict[str, int] = {}
    for line in docstring.splitlines():
        line = line.strip()
        m = re.match(r"^([^:()]+?)\s*\((\d+)\):\s*.+$", line)
        if m:
            category = m.group(1).strip()
            count = int(m.group(2))
            categories[category] = count
    return categories


def _relative_paths(paths: Iterable[Path]) -> List[str]:
    return sorted(str(p.relative_to(project_root)) for p in paths)


def get_mcp_tool_surface() -> Dict[str, Any]:
    """Return MCP tools/list and tools/call surfaces and parity details."""
    content = _read_lucid_mcp_content()

    list_block = _extract_bracket_block(content, "all_tools = [")
    call_block = _extract_handle_tools_call_block(content)
    header_doc = _extract_header_docstring(content)

    listed_tools: Set[str] = set(
        re.findall(r'"name"\s*:\s*"([a-zA-Z0-9_\-]+)"', list_block)
    )
    callable_tools: Set[str] = set(
        re.findall(r'tool_name\s*==\s*"([a-zA-Z0-9_\-]+)"', call_block)
    )

    header_match = re.search(r"AIM-OS Tools \((\d+) total\):", header_doc)
    header_count = int(header_match.group(1)) if header_match else None

    only_listed = sorted(listed_tools - callable_tools)
    only_callable = sorted(callable_tools - listed_tools)
    parity_ok = not only_listed and not only_callable

    return {
        "count": len(listed_tools),
        "listed_count": len(listed_tools),
        "callable_count": len(callable_tools),
        "header_count": header_count,
        "parity_ok": parity_ok,
        "listed_not_callable": only_listed,
        "callable_not_listed": only_callable,
        "categories": _extract_header_categories(header_doc),
        "source": "lucid_mcp_server.py",
        "detection_method": "balanced all_tools parse + handle_tools_call parse",
        "last_updated": _now_iso(),
    }


def detect_cursor_command_count() -> Dict[str, Any]:
    commands_dir = project_root / ".cursor" / "commands"
    if not commands_dir.exists():
        return {
            "count": 0,
            "error": ".cursor/commands/ not found",
            "source": ".cursor/commands/",
            "last_updated": _now_iso(),
        }

    command_files = sorted(commands_dir.glob("*.md"))
    return {
        "count": len(command_files),
        "files": [f.name for f in command_files],
        "source": ".cursor/commands/",
        "detection_method": "*.md file count",
        "last_updated": _now_iso(),
    }


def detect_system_count() -> Dict[str, Any]:
    packages_dir = project_root / "packages"
    if not packages_dir.exists():
        return {
            "count": 0,
            "error": "packages/ not found",
            "source": "packages/",
            "last_updated": _now_iso(),
        }

    systems = sorted(
        d.name
        for d in packages_dir.iterdir()
        if d.is_dir()
        and not d.name.startswith("_")
        and not d.name.startswith(".")
        and not d.name.endswith(".egg-info")
    )

    return {
        "count": len(systems),
        "systems": systems,
        "source": "packages/",
        "detection_method": "directory count (excluding dot/underscore/egg-info)",
        "last_updated": _now_iso(),
    }


def detect_documentation_count() -> Dict[str, Any]:
    docs_patterns = [
        "knowledge_architecture/**/*.md",
        "cursor-addon/docs/**/*.md",
        "*.md",
    ]

    by_location: Dict[str, int] = {}
    all_docs: Set[Path] = set()

    for pattern in docs_patterns:
        files = [
            f
            for f in project_root.glob(pattern)
            if "node_modules" not in str(f) and ".git" not in str(f)
        ]
        by_location[pattern] = len(files)
        all_docs.update(files)

    return {
        "total_files": len(all_docs),
        "by_location": by_location,
        "source": "knowledge_architecture/ + cursor-addon/docs/ + root",
        "detection_method": "deduped *.md file count",
        "last_updated": _now_iso(),
    }


def detect_test_count() -> Dict[str, Any]:
    test_patterns = [
        "**/test_*.py",
        "**/*_test.py",
        "**/tests/**/*.py",
    ]

    test_files: Set[Path] = set()
    for pattern in test_patterns:
        files = [
            f
            for f in project_root.glob(pattern)
            if "node_modules" not in str(f) and ".git" not in str(f)
        ]
        test_files.update(files)

    return {
        "total": len(test_files),
        "test_files": len(test_files),
        "files": _relative_paths(test_files),
        "source": "**/test_*.py + **/*_test.py + **/tests/**/*.py",
        "detection_method": "deduped test file pattern matching",
        "last_updated": _now_iso(),
    }


def generate_source_of_truth(output_path: Path | None = None) -> Dict[str, Any]:
    if output_path is None:
        output_path = project_root / "SOURCE_OF_TRUTH.yaml"

    source_of_truth = {
        "aim_os_source_of_truth": {
            "version": "1.1.0",
            "generated": _now_iso(),
            "note": "Auto-generated from code - DO NOT EDIT MANUALLY",
            "mcp_tools": get_mcp_tool_surface(),
            "cursor_commands": detect_cursor_command_count(),
            "systems": detect_system_count(),
            "documentation": detect_documentation_count(),
            "tests": detect_test_count(),
        }
    }

    with output_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(source_of_truth, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    mcp = source_of_truth["aim_os_source_of_truth"]["mcp_tools"]
    print(f"[OK] Source of truth generated: {output_path}")
    print(f"   MCP Tools (listed): {mcp['listed_count']}")
    print(f"   MCP Tools (callable): {mcp['callable_count']}")
    print(f"   MCP Parity OK: {mcp['parity_ok']}")
    print(f"   Cursor Commands: {source_of_truth['aim_os_source_of_truth']['cursor_commands']['count']}")
    print(f"   Systems: {source_of_truth['aim_os_source_of_truth']['systems']['count']}")
    print(f"   Documentation Files: {source_of_truth['aim_os_source_of_truth']['documentation']['total_files']}")
    print(f"   Test Files: {source_of_truth['aim_os_source_of_truth']['tests']['total']}")

    return source_of_truth


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect source of truth from code")
    parser.add_argument("--output", type=Path, default=None, help="Output path for SOURCE_OF_TRUTH.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Show preview without writing file")
    parser.add_argument(
        "--check-mcp-parity",
        action="store_true",
        help="Exit non-zero if tools/list and tools/call are out of parity",
    )
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN - Detecting source of truth...")
        mcp = get_mcp_tool_surface()
        commands = detect_cursor_command_count()
        systems = detect_system_count()
        docs = detect_documentation_count()
        tests = detect_test_count()

        print("\nSource of Truth Preview:")
        print(f"   MCP Tools (listed): {mcp['listed_count']}")
        print(f"   MCP Tools (callable): {mcp['callable_count']}")
        print(f"   MCP Parity OK: {mcp['parity_ok']}")
        print(f"   Cursor Commands: {commands['count']}")
        print(f"   Systems: {systems['count']}")
        print(f"   Documentation Files: {docs['total_files']}")
        print(f"   Test Files: {tests['total']}")
        if not mcp["parity_ok"]:
            print(f"   Listed not callable: {mcp['listed_not_callable']}")
            print(f"   Callable not listed: {mcp['callable_not_listed']}")
    else:
        generate_source_of_truth(args.output)

    if args.check_mcp_parity:
        mcp = get_mcp_tool_surface()
        if not mcp["parity_ok"]:
            print("[FAIL] MCP tool parity check failed.")
            print(f"       Listed not callable: {mcp['listed_not_callable']}")
            print(f"       Callable not listed: {mcp['callable_not_listed']}")
            raise SystemExit(1)
        print("[OK] MCP tool parity check passed.")


if __name__ == "__main__":
    main()
