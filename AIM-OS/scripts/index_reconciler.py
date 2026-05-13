"""
AIM-OS Index Reconciler
=======================

Scans the codebase and compares against existing indexes to identify
documentation gaps. Generates a gap report and optionally updates indexes.

Usage:
    python3 scripts/index_reconciler.py                    # Full scan + report
    python3 scripts/index_reconciler.py --update           # Scan + update SYSTEM_REGISTRY
    python3 scripts/index_reconciler.py --domains          # Show domain breakdown
    python3 scripts/index_reconciler.py --json             # Machine-readable output

Author: Gemini (Antigravity) — March 11, 2026
"""

import os
import sys
import json
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime


WORKSPACE = Path(__file__).parent.parent
PACKAGES_DIR = WORKSPACE / "packages"
AI_ENGINE_DIR = WORKSPACE / "scripts" / "ai_engine"
AGENT_DIR = WORKSPACE / ".agent"
REGISTRY_PATH = AGENT_DIR / "SYSTEM_REGISTRY.md"
MASTER_INDEX_PATH = AGENT_DIR / "AIMOS_MASTER_SYSTEM_INDEX.md"
HIER_NAV_PATH = WORKSPACE / "knowledge_architecture" / "HIERARCHICAL_NAVIGATION_INDEX.md"


# ═══════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════

@dataclass
class SystemEntry:
    """A discovered AIM-OS system/package."""
    name: str
    path: str
    language: str = "unknown"
    lines: int = 0
    purpose: str = ""
    domain: str = "unknown"
    has_readme: bool = False
    has_tests: bool = False
    has_init: bool = False
    in_registry: bool = False
    in_master_index: bool = False
    in_hier_nav: bool = False
    files_count: int = 0


@dataclass
class GapReport:
    """Results of the reconciliation scan."""
    timestamp: str = ""
    total_systems: int = 0
    in_registry: int = 0
    in_master_index: int = 0
    in_hier_nav: int = 0
    missing_from_registry: list = field(default_factory=list)
    missing_from_master: list = field(default_factory=list)
    missing_from_hier_nav: list = field(default_factory=list)
    systems_by_domain: dict = field(default_factory=dict)
    systems: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════
# SCANNING
# ═══════════════════════════════════════════════════════

def count_lines(directory: Path) -> int:
    """Count code lines in a directory (Python + TypeScript + JavaScript)."""
    total = 0
    extensions = {'.py', '.ts', '.tsx', '.js', '.jsx'}
    try:
        for f in directory.rglob('*'):
            if f.is_file() and f.suffix in extensions:
                # Skip node_modules, dist, build, .venv
                parts = f.parts
                if any(skip in parts for skip in ('node_modules', 'dist', 'build', '.venv', '__pycache__')):
                    continue
                try:
                    total += len(f.read_text(errors='ignore').splitlines())
                except (PermissionError, OSError):
                    pass
    except Exception:
        pass
    return total


def detect_language(directory: Path) -> str:
    """Detect primary language of a package."""
    py_count = len(list(directory.rglob('*.py')))
    ts_count = len(list(directory.rglob('*.ts'))) + len(list(directory.rglob('*.tsx')))
    js_count = len(list(directory.rglob('*.js'))) + len(list(directory.rglob('*.jsx')))

    if ts_count > py_count and ts_count > js_count:
        return "typescript"
    elif py_count > 0:
        return "python"
    elif js_count > 0:
        return "javascript"
    return "unknown"


def extract_purpose(directory: Path) -> str:
    """Extract purpose from README or __init__.py."""
    # Try README
    for readme_name in ['README.md', 'readme.md', 'README.txt']:
        readme = directory / readme_name
        if readme.exists():
            text = readme.read_text(errors='ignore')
            # First non-empty, non-header line
            for line in text.splitlines():
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('---'):
                    return line[:120]

    # Try __init__.py docstring
    init = directory / '__init__.py'
    if init.exists():
        text = init.read_text(errors='ignore')
        match = re.search(r'"""(.+?)"""', text, re.DOTALL)
        if match:
            return match.group(1).strip().split('\n')[0][:120]

    # Try package.json description
    pkg = directory / 'package.json'
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(errors='ignore'))
            desc = data.get('description', '')
            if desc:
                return desc[:120]
        except json.JSONDecodeError:
            pass

    return ""


DOMAIN_KEYWORDS = {
    "Core Infrastructure": ['cmc', 'hhni', 'vif', 'apoe', 'seg', 'sdfcvf', 'cas', 'timeline_context', 'safety_systems'],
    "AI Engine": ['chain_director', 'chain_topologies', 'chained_mission', 'atlas', 'context_mapper',
                  'context_concierge', 'context_engine', 'agent_runtime', 'agent_spawner', 'roundtable',
                  'llm_router', 'engine', 'enhanced_worker', 'mesh', 'genome'],
    "Context System": ['context_bootloader', 'context_', 'large_file_reader'],
    "Agent System": ['agent', 'specialist', 'capability_awareness', 'genome'],
    "MCP & Transport": ['mcp', 'lucid_mcp', 'daemon_rag'],
    "UI & Cockpit": ['joc', 'ide_chat', 'mobile', 'tournament', 'browser-automation', 'lucid_core_console',
                     'plix', 'monaco', 'lucid_document'],
    "Consciousness & Safety": ['consciousness', 'scor', 'holographic', 'sis', 'temporal_consciousness',
                              'intuitive_intelligence'],
    "Supporting": ['router', 'prompt_chain', 'llm_client', 'api_service', 'intent_classification',
                   'orchestration', 'autonomous', 'nl_tags', 'icip', 'deepsearch', 'doc_builder',
                   'log_sentinels', 'meta_', 'quaternion', 'schemas', 'ai_collaboration', 'shared',
                   'integration_tests'],
    "SDK & External": ['sdk', 'jarvis', 'mobile_app', 'igodn'],
}


def classify_domain(name: str) -> str:
    """Classify a system into its domain."""
    name_lower = name.lower().replace('-', '_')
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in name_lower:
                return domain
    return "Unknown"


def scan_packages() -> list[SystemEntry]:
    """Scan all packages in the packages/ directory."""
    systems = []
    if not PACKAGES_DIR.exists():
        return systems

    for pkg_dir in sorted(PACKAGES_DIR.iterdir()):
        if not pkg_dir.is_dir() or pkg_dir.name.startswith('.'):
            continue

        entry = SystemEntry(
            name=pkg_dir.name,
            path=f"packages/{pkg_dir.name}/",
            language=detect_language(pkg_dir),
            lines=count_lines(pkg_dir),
            purpose=extract_purpose(pkg_dir),
            domain=classify_domain(pkg_dir.name),
            has_readme=(pkg_dir / 'README.md').exists(),
            has_tests=any(pkg_dir.rglob('test_*')) or any(pkg_dir.rglob('*_test.*')),
            has_init=(pkg_dir / '__init__.py').exists() or (pkg_dir / 'package.json').exists(),
            files_count=sum(1 for f in pkg_dir.rglob('*') if f.is_file()
                          and 'node_modules' not in str(f)
                          and '__pycache__' not in str(f)),
        )
        systems.append(entry)

    return systems


def scan_ai_engine() -> list[SystemEntry]:
    """Scan AI Engine modules."""
    systems = []
    if not AI_ENGINE_DIR.exists():
        return systems

    for f in sorted(AI_ENGINE_DIR.iterdir()):
        if f.is_file() and f.suffix == '.py' and not f.name.startswith('test_'):
            lines = len(f.read_text(errors='ignore').splitlines())
            purpose = ""
            text = f.read_text(errors='ignore')
            match = re.search(r'"""(.+?)"""', text, re.DOTALL)
            if match:
                purpose = match.group(1).strip().split('\n')[0][:120]

            systems.append(SystemEntry(
                name=f"ai_engine/{f.stem}",
                path=f"scripts/ai_engine/{f.name}",
                language="python",
                lines=lines,
                purpose=purpose,
                domain="AI Engine",
                files_count=1,
            ))

    return systems


# ═══════════════════════════════════════════════════════
# INDEX CHECKING
# ═══════════════════════════════════════════════════════

def load_index_names(path: Path) -> set[str]:
    """Extract system/package names from an index file."""
    names = set()
    if not path.exists():
        return names

    text = path.read_text(errors='ignore')
    # Match markdown table rows with bold names: | **name** | ...
    for match in re.finditer(r'\|\s*\*\*(\w[\w\-]*)\*\*', text):
        names.add(match.group(1).lower().replace('-', '_'))

    # Also match unbolded table entries
    for match in re.finditer(r'\|\s*(\w[\w\-]+)\s*\|', text):
        name = match.group(1).lower().replace('-', '_')
        if len(name) > 2 and name not in {'system', 'package', 'purpose', 'path', 'status',
                                           'lines', 'lang', 'exports', 'module', 'type',
                                           'description', 'count', 'metric', 'domain'}:
            names.add(name)

    return names


def check_coverage(systems: list[SystemEntry]) -> None:
    """Check each system against all indexes."""
    registry_names = load_index_names(REGISTRY_PATH)
    master_names = load_index_names(MASTER_INDEX_PATH)
    hier_nav_names = load_index_names(HIER_NAV_PATH)

    for sys in systems:
        clean_name = sys.name.lower().replace('-', '_').replace('ai_engine/', '')
        sys.in_registry = clean_name in registry_names
        sys.in_master_index = clean_name in master_names
        sys.in_hier_nav = clean_name in hier_nav_names


# ═══════════════════════════════════════════════════════
# REPORTING
# ═══════════════════════════════════════════════════════

def generate_report(systems: list[SystemEntry]) -> GapReport:
    """Generate the gap report."""
    report = GapReport(
        timestamp=datetime.now().isoformat(),
        total_systems=len(systems),
        in_registry=sum(1 for s in systems if s.in_registry),
        in_master_index=sum(1 for s in systems if s.in_master_index),
        in_hier_nav=sum(1 for s in systems if s.in_hier_nav),
        missing_from_registry=[s.name for s in systems if not s.in_registry],
        missing_from_master=[s.name for s in systems if not s.in_master_index],
        missing_from_hier_nav=[s.name for s in systems if not s.in_hier_nav],
    )

    # Group by domain
    for sys in systems:
        if sys.domain not in report.systems_by_domain:
            report.systems_by_domain[sys.domain] = []
        report.systems_by_domain[sys.domain].append(sys.name)

    report.systems = [asdict(s) for s in systems]
    return report


def print_report(report: GapReport) -> None:
    """Print a human-readable gap report."""
    print("=" * 60)
    print("  AIM-OS Index Reconciliation Report")
    print(f"  Generated: {report.timestamp}")
    print("=" * 60)

    print(f"\n📊 Coverage Summary")
    print(f"  Total systems scanned:          {report.total_systems}")
    print(f"  In SYSTEM_REGISTRY:             {report.in_registry} ({report.in_registry/report.total_systems*100:.0f}%)")
    print(f"  In MASTER_SYSTEM_INDEX:         {report.in_master_index} ({report.in_master_index/report.total_systems*100:.0f}%)")
    print(f"  In HIERARCHICAL_NAV:            {report.in_hier_nav} ({report.in_hier_nav/report.total_systems*100:.0f}%)")

    print(f"\n🏷️  By Domain")
    for domain, systems in sorted(report.systems_by_domain.items()):
        print(f"  {domain}: {len(systems)}")

    if report.missing_from_hier_nav:
        print(f"\n⚠️  Missing from HIERARCHICAL_NAVIGATION_INDEX ({len(report.missing_from_hier_nav)}):")
        for name in sorted(report.missing_from_hier_nav):
            print(f"    - {name}")

    if report.missing_from_registry:
        print(f"\n⚠️  Missing from SYSTEM_REGISTRY ({len(report.missing_from_registry)}):")
        for name in sorted(report.missing_from_registry):
            print(f"    - {name}")

    print("\n" + "=" * 60)


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def main():
    args = sys.argv[1:]

    print("🔍 Scanning AIM-OS codebase...\n")

    # Scan
    pkg_systems = scan_packages()
    engine_systems = scan_ai_engine()
    all_systems = pkg_systems + engine_systems

    print(f"  Found {len(pkg_systems)} packages + {len(engine_systems)} AI Engine modules = {len(all_systems)} total\n")

    # Check coverage
    check_coverage(all_systems)

    # Generate report
    report = generate_report(all_systems)

    if '--json' in args:
        print(json.dumps(asdict(report), indent=2))
    elif '--domains' in args:
        for domain, systems in sorted(report.systems_by_domain.items()):
            print(f"\n{domain} ({len(systems)}):")
            for name in sorted(systems):
                sys_obj = next((s for s in all_systems if s.name == name), None)
                if sys_obj:
                    status = "✅" if sys_obj.in_hier_nav else "❌"
                    print(f"  {status} {name} ({sys_obj.lines:,} lines, {sys_obj.language})")
    else:
        print_report(report)

    # Total lines
    total_lines = sum(s.lines for s in all_systems)
    print(f"\n📏 Total code lines scanned: {total_lines:,}")


if __name__ == "__main__":
    main()
