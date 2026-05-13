"""
Documentation Engine — Automated T0 Generator

This script does what AGENT-DOCS would do:
1. Scans all packages in packages/
2. Identifies which have no system docs
3. Reads the code structure (modules, classes, functions)
4. Generates T0 executive summaries using code analysis
5. Saves them to knowledge_architecture/systems/{name}/

Usage:
    python scripts/ai_engine/docs_engine.py audit       # Show coverage
    python scripts/ai_engine/docs_engine.py generate     # Generate missing T0s
    python scripts/ai_engine/docs_engine.py parity       # Check doc-code parity

Part of the AGENT-DOCS specialist system.
"""

import os
import sys
import ast
import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# ─────────────────────────────────────────────────────────────
# Package-to-System Naming Map (imported from agent_spawner)
# ─────────────────────────────────────────────────────────────

try:
    from agent_spawner import PACKAGE_TO_SYSTEM_MAP
except ImportError:
    PACKAGE_TO_SYSTEM_MAP = {
        "cas": "cognitive_analysis",
        "cmc_service": "cmc",
        "llm_client": "llm_client_integration",
        "ai_collaboration": "ai_collaboration_system",
        "autonomous_protocol": "autonomous_research_dream",
        "agent": "agent_system",
        "context_bootloader": "knowledge_bootstrap_system",
    }

SKIP_PACKAGES = {
    "__pycache__", "cmc_service.egg-info", "integration_tests",
    "schemas", "shared", "node_modules", ".git",
}

# ─────────────────────────────────────────────────────────────
# Code Analysis
# ─────────────────────────────────────────────────────────────

@dataclass
class ModuleInfo:
    """Info about a single Python module."""
    name: str
    path: str
    docstring: str = ""
    classes: list = field(default_factory=list)
    functions: list = field(default_factory=list)
    lines: int = 0

@dataclass
class PackageInfo:
    """Info about a package."""
    name: str
    path: str
    modules: list = field(default_factory=list)
    total_lines: int = 0
    total_classes: int = 0
    total_functions: int = 0
    has_tests: bool = False
    has_readme: bool = False
    languages: list = field(default_factory=list)
    docstring: str = ""

def analyze_python_module(filepath: str) -> Optional[ModuleInfo]:
    """Analyze a Python module for classes, functions, and docstrings."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except (UnicodeDecodeError, OSError):
        return None
    
    info = ModuleInfo(
        name=Path(filepath).stem,
        path=filepath,
        lines=source.count("\n") + 1,
    )
    
    try:
        tree = ast.parse(source)
        # Module docstring
        if (tree.body and isinstance(tree.body[0], ast.Expr) and 
            isinstance(tree.body[0].value, (ast.Constant, ast.Str))):
            info.docstring = getattr(tree.body[0].value, 'value', 
                                     getattr(tree.body[0].value, 's', ''))
        
        # Classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node) or ""
                info.classes.append({
                    "name": node.name,
                    "doc": doc[:120],
                    "methods": len([n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]),
                })
            elif isinstance(node, ast.FunctionDef) and not isinstance(getattr(node, '_parent', None), ast.ClassDef):
                # Top-level functions only
                if node.col_offset == 0:
                    doc = ast.get_docstring(node) or ""
                    info.functions.append({"name": node.name, "doc": doc[:120]})
    except SyntaxError:
        pass
    
    return info

def analyze_package(pkg_path: str) -> PackageInfo:
    """Analyze a package directory."""
    name = Path(pkg_path).name
    info = PackageInfo(name=name, path=pkg_path)
    
    # Check for README
    info.has_readme = os.path.exists(os.path.join(pkg_path, "README.md"))
    
    # Check for tests
    info.has_tests = os.path.isdir(os.path.join(pkg_path, "tests")) or \
                     any(f.startswith("test_") for f in os.listdir(pkg_path) if os.path.isfile(os.path.join(pkg_path, f)))
    
    # Detect languages
    files = []
    for root, _dirs, fnames in os.walk(pkg_path):
        # Skip deep directories
        depth = root.replace(pkg_path, "").count(os.sep)
        if depth > 3:
            continue
        for f in fnames:
            files.append(os.path.join(root, f))
    
    py_files = [f for f in files if f.endswith(".py") and "__pycache__" not in f]
    ts_files = [f for f in files if f.endswith((".ts", ".tsx")) and "node_modules" not in f]
    
    if py_files:
        info.languages.append("Python")
    if ts_files:
        info.languages.append("TypeScript")
    
    # Analyze Python modules
    for py_file in py_files:
        mod = analyze_python_module(py_file)
        if mod:
            info.modules.append(mod)
            info.total_lines += mod.lines
            info.total_classes += len(mod.classes)
            info.total_functions += len(mod.functions)
    
    # For TypeScript, just count files and lines
    for ts_file in ts_files:
        try:
            with open(ts_file, "r", encoding="utf-8") as f:
                info.total_lines += f.read().count("\n") + 1
        except (UnicodeDecodeError, OSError):
            pass
    
    # Package docstring from __init__.py
    init_path = os.path.join(pkg_path, "__init__.py")
    if os.path.exists(init_path):
        mod = analyze_python_module(init_path)
        if mod and mod.docstring:
            info.docstring = mod.docstring
    
    return info


# ─────────────────────────────────────────────────────────────
# T0 Generator
# ─────────────────────────────────────────────────────────────

def generate_t0(info: PackageInfo) -> str:
    """Generate a T0 executive summary from package analysis."""
    
    # Build description from code analysis
    class_names = []
    for mod in info.modules:
        for cls in mod.classes:
            class_names.append(f"**{cls['name']}**")
    
    # Use package docstring or infer description
    if info.docstring:
        description = info.docstring.strip().split("\n")[0]
    elif class_names:
        description = f"Package containing {', '.join(class_names[:5])}"
        if len(class_names) > 5:
            description += f" and {len(class_names)-5} more classes"
    else:
        description = f"Package with {info.total_lines} lines across {len(info.modules)} modules"
    
    # Build component listing 
    components = []
    for mod in info.modules:
        if mod.name.startswith("_") or mod.name == "__init__":
            continue
        if mod.classes:
            for cls in mod.classes[:3]:
                doc = cls['doc'].split('\n')[0] if cls['doc'] else f"{cls['methods']} methods"
                components.append(f"**{cls['name']}** ({doc})")
        elif mod.functions:
            components.append(f"**{mod.name}** module ({len(mod.functions)} functions)")
    
    components_str = ", ".join(components[:8])
    if len(components) > 8:
        components_str += f", and {len(components)-8} more"
    
    lang_str = "/".join(info.languages) if info.languages else "Unknown"
    tests_str = "Tests exist" if info.has_tests else "No tests found"
    
    return f"""---
id: "{info.name}_T0_executive"
system: "{info.name}"
level: "T0"
type: "executive"
title: "{info.name} Executive Summary"
description: "Auto-generated executive summary of {info.name}"
confidence_threshold: 0.70
token_cost: 100
created: "{datetime.now().strftime('%Y-%m-%d')}"
author: "docs-engine"
status: "draft"
tags: ["{info.name}", "t0-t6", "auto-generated"]
---

# {info.name} — Executive Summary

{description}

Components: {components_str if components_str else 'See modules below'}.
Language: {lang_str}. Lines: {info.total_lines:,}. Classes: {info.total_classes}. Functions: {info.total_functions}. {tests_str}.
"""


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

def find_undocumented_packages(root: str) -> list:
    """Find packages that have no matching system docs."""
    pkg_dir = os.path.join(root, "packages")
    sys_dir = os.path.join(root, "knowledge_architecture", "systems")
    
    if not os.path.isdir(pkg_dir) or not os.path.isdir(sys_dir):
        print("Error: packages/ or knowledge_architecture/systems/ not found")
        return []
    
    system_dirs = set(os.listdir(sys_dir))
    undocumented = []
    
    for pkg_name in sorted(os.listdir(pkg_dir)):
        pkg_path = os.path.join(pkg_dir, pkg_name)
        if not os.path.isdir(pkg_path) or pkg_name in SKIP_PACKAGES:
            continue
        
        # Check naming map first
        mapped = PACKAGE_TO_SYSTEM_MAP.get(pkg_name)
        if mapped is None and pkg_name in PACKAGE_TO_SYSTEM_MAP:
            continue  # Explicitly mapped to None (no docs needed)
        
        # Check if system docs exist
        search_name = mapped or pkg_name
        sys_path = os.path.join(sys_dir, search_name)
        
        if os.path.isdir(sys_path):
            # Check if T0 exists
            has_t0 = os.path.exists(os.path.join(sys_path, "T0_executive.md"))
            has_l0 = os.path.exists(os.path.join(sys_path, "L0_executive.md"))
            if has_t0 or has_l0:
                continue
        
        undocumented.append({
            "package": pkg_name,
            "path": pkg_path,
            "expected_system": search_name,
        })
    
    return undocumented


def cmd_audit(root: str):
    """Run documentation coverage audit."""
    undocumented = find_undocumented_packages(root)
    
    print("=" * 60)
    print("  DOCS ENGINE — Coverage Audit")
    print("=" * 60)
    
    pkg_dir = os.path.join(root, "packages")
    total = len([d for d in os.listdir(pkg_dir) 
                 if os.path.isdir(os.path.join(pkg_dir, d)) and d not in SKIP_PACKAGES])
    
    print(f"\n  Total packages:     {total}")
    print(f"  Documented:         {total - len(undocumented)}")
    print(f"  Undocumented:       {len(undocumented)}")
    print(f"  Coverage:           {100*(total-len(undocumented))//total}%")
    
    if undocumented:
        print(f"\n{'Package':30s} {'Expected System Dir':30s}")
        print("-" * 62)
        for item in undocumented:
            print(f"  {item['package']:28s} {item['expected_system']:28s}")
    
    print()


def cmd_generate(root: str, dry_run: bool = False):
    """Generate T0 executive summaries for undocumented packages."""
    undocumented = find_undocumented_packages(root)
    
    if not undocumented:
        print("All packages have documentation!")
        return
    
    print("=" * 60)
    print("  DOCS ENGINE — Auto-Generating T0 Summaries")
    print("=" * 60)
    
    generated = 0
    skipped = 0
    
    for item in undocumented:
        pkg_info = analyze_package(item["path"])
        
        # Skip tiny packages
        if pkg_info.total_lines < 10 and not pkg_info.modules:
            print(f"  SKIP {item['package']:28s} (too small: {pkg_info.total_lines} lines)")
            skipped += 1
            continue
        
        t0_content = generate_t0(pkg_info)
        
        # Target path
        sys_path = os.path.join(root, "knowledge_architecture", "systems", item["expected_system"])
        t0_path = os.path.join(sys_path, "T0_executive.md")
        
        if dry_run:
            print(f"  WOULD {item['package']:28s} → {item['expected_system']}/T0_executive.md")
            print(f"    Lines: {pkg_info.total_lines}, Classes: {pkg_info.total_classes}, "
                  f"Functions: {pkg_info.total_functions}")
        else:
            os.makedirs(sys_path, exist_ok=True)
            with open(t0_path, "w", encoding="utf-8") as f:
                f.write(t0_content)
            print(f"  ✅ {item['package']:28s} → {item['expected_system']}/T0_executive.md "
                  f"({pkg_info.total_lines} lines, {pkg_info.total_classes} classes)")
        
        generated += 1
    
    print(f"\n  Generated: {generated}, Skipped: {skipped}")


def cmd_parity(root: str):
    """Check doc-code parity — are docs accurate?"""
    pkg_dir = os.path.join(root, "packages")
    sys_dir = os.path.join(root, "knowledge_architecture", "systems")
    
    print("=" * 60)
    print("  DOCS ENGINE — Doc-Code Parity Check")
    print("=" * 60)
    
    checked = 0
    in_parity = 0
    gaps = []
    
    for pkg_name in sorted(os.listdir(pkg_dir)):
        pkg_path = os.path.join(pkg_dir, pkg_name)
        if not os.path.isdir(pkg_path) or pkg_name in SKIP_PACKAGES:
            continue
        
        # Find matching system docs
        mapped = PACKAGE_TO_SYSTEM_MAP.get(pkg_name, pkg_name)
        if mapped is None:
            continue
        
        sys_path = os.path.join(sys_dir, mapped)
        t0_path = os.path.join(sys_path, "T0_executive.md")
        l0_path = os.path.join(sys_path, "L0_executive.md")
        
        if not os.path.exists(t0_path) and not os.path.exists(l0_path):
            continue
        
        checked += 1
        
        # Read doc content
        doc_path = t0_path if os.path.exists(t0_path) else l0_path
        try:
            with open(doc_path, "r", encoding="utf-8") as f:
                doc_content = f.read().lower()
        except (UnicodeDecodeError, OSError):
            continue
        
        # Analyze package
        pkg_info = analyze_package(pkg_path)
        
        # Check: do main classes appear in docs?
        main_classes = [cls["name"].lower() for mod in pkg_info.modules for cls in mod.classes]
        found = sum(1 for c in main_classes if c in doc_content)
        
        if main_classes and found / len(main_classes) >= 0.3:
            in_parity += 1
        elif main_classes:
            missing = [c for c in main_classes if c not in doc_content]
            gaps.append({
                "package": pkg_name,
                "system": mapped,
                "missing_classes": missing[:5],
                "coverage": f"{100*found//len(main_classes)}%",
            })
    
    print(f"\n  Packages with docs checked: {checked}")
    print(f"  In parity:                  {in_parity}")
    print(f"  Gaps found:                 {len(gaps)}")
    
    if gaps:
        print(f"\n{'Package':25s} {'System':25s} {'Coverage':10s} Missing Classes")
        print("-" * 90)
        for g in gaps[:15]:
            missing = ", ".join(g["missing_classes"][:3])
            print(f"  {g['package']:23s} {g['system']:23s} {g['coverage']:8s} {missing}")


def generate_code_appendix(info: PackageInfo) -> str:
    """Generate a code structure appendix to append to existing docs."""
    lines = []
    lines.append("\n\n---\n")
    lines.append("## Code Structure (auto-generated by docs-engine)\n")
    lines.append(f"\n**Package:** `{info.name}` | "
                 f"**Lines:** {info.total_lines:,} | "
                 f"**Classes:** {info.total_classes} | "
                 f"**Functions:** {info.total_functions}\n")
    
    for mod in sorted(info.modules, key=lambda m: m.name):
        if mod.name.startswith("_") and mod.name != "__init__":
            continue
        if not mod.classes and not mod.functions:
            continue
        
        lines.append(f"\n### `{mod.name}.py` ({mod.lines} lines)\n")
        
        for cls in mod.classes:
            doc = cls['doc'].split('\n')[0] if cls['doc'] else ""
            if doc:
                lines.append(f"- **{cls['name']}** — {doc}")
            else:
                lines.append(f"- **{cls['name']}** ({cls['methods']} methods)")
        
        for fn in mod.functions:
            doc = fn['doc'].split('\n')[0] if fn['doc'] else ""
            if doc:
                lines.append(f"- `{fn['name']}()` — {doc}")
            else:
                lines.append(f"- `{fn['name']}()`")
    
    return "\n".join(lines) + "\n"


def cmd_enrich(root: str, dry_run: bool = False):
    """Enrich existing docs with code structure appendices."""
    pkg_dir = os.path.join(root, "packages")
    sys_dir = os.path.join(root, "knowledge_architecture", "systems")
    
    print("=" * 60)
    print("  DOCS ENGINE — Enriching Docs with Code Structure")
    print("=" * 60)
    
    enriched = 0
    skipped = 0
    already = 0
    
    for pkg_name in sorted(os.listdir(pkg_dir)):
        pkg_path = os.path.join(pkg_dir, pkg_name)
        if not os.path.isdir(pkg_path) or pkg_name in SKIP_PACKAGES:
            continue
        
        # Find matching system docs
        mapped = PACKAGE_TO_SYSTEM_MAP.get(pkg_name, pkg_name)
        if mapped is None:
            continue
        
        sys_path = os.path.join(sys_dir, mapped)
        t0_path = os.path.join(sys_path, "T0_executive.md")
        l0_path = os.path.join(sys_path, "L0_executive.md")
        
        # Find the doc to enrich
        doc_path = t0_path if os.path.exists(t0_path) else (l0_path if os.path.exists(l0_path) else None)
        if not doc_path:
            continue
        
        # Read existing content
        try:
            with open(doc_path, "r", encoding="utf-8") as f:
                existing = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        
        # Skip if already enriched
        if "auto-generated by docs-engine" in existing:
            already += 1
            continue
        
        # Analyze package
        pkg_info = analyze_package(pkg_path)
        
        # Skip if no classes/functions to document
        if pkg_info.total_classes == 0 and pkg_info.total_functions == 0:
            skipped += 1
            continue
        
        # Check parity — skip if docs already mention most classes
        main_classes = [cls["name"].lower() for mod in pkg_info.modules for cls in mod.classes]
        if main_classes:
            found = sum(1 for c in main_classes if c in existing.lower())
            if found / len(main_classes) >= 0.5:
                skipped += 1
                continue
        
        # Generate appendix
        appendix = generate_code_appendix(pkg_info)
        
        if dry_run:
            print(f"  WOULD  {pkg_name:28s} +{len(appendix)} chars "
                  f"({pkg_info.total_classes} classes, {pkg_info.total_functions} fns)")
        else:
            with open(doc_path, "a", encoding="utf-8") as f:
                f.write(appendix)
            print(f"  ✅ {pkg_name:28s} +{len(appendix):>5} chars "
                  f"({pkg_info.total_classes} cls, {pkg_info.total_functions} fns)")
        
        enriched += 1
    
    print(f"\n  Enriched: {enriched}, Skipped: {skipped}, Already done: {already}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AIM-OS Documentation Engine")
    parser.add_argument("command", choices=["audit", "generate", "parity", "enrich"],
                       help="Command to run")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without writing")
    args = parser.parse_args()
    
    # Find AIM-OS root
    root = str(Path(__file__).parent.parent.parent)
    
    if args.command == "audit":
        cmd_audit(root)
    elif args.command == "generate":
        cmd_generate(root, dry_run=args.dry_run)
    elif args.command == "parity":
        cmd_parity(root)
    elif args.command == "enrich":
        cmd_enrich(root, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
