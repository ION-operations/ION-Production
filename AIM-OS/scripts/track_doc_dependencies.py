#!/usr/bin/env python3
"""
Track Document Dependencies

Scans all documentation files, extracts dependencies from metadata,
builds dependency graph, and updates cross_system_connections.yaml.

Usage:
    python scripts/track_doc_dependencies.py
    python scripts/track_doc_dependencies.py --dry-run
    python scripts/track_doc_dependencies.py --update-yaml
"""

import argparse
import sys
import re
import yaml
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """Parse YAML frontmatter from markdown file"""
    # Match frontmatter between --- delimiters
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    
    if not match:
        return {}, content
    
    frontmatter_text = match.group(1)
    body = match.group(2)
    
    try:
        metadata = yaml.safe_load(frontmatter_text) or {}
        return metadata, body
    except yaml.YAMLError:
        return {}, content


def find_all_docs() -> List[Path]:
    """Find all markdown documentation files"""
    doc_patterns = [
        "knowledge_architecture/**/*.md",
        "cursor-addon/docs/**/*.md",
        "*.md"
    ]
    
    docs = []
    for pattern in doc_patterns:
        files = list(project_root.glob(pattern))
        # Filter out node_modules, .git, etc.
        files = [f for f in files if 'node_modules' not in str(f) and '.git' not in str(f)]
        docs.extend(files)
    
    # Remove duplicates
    return list(set(docs))


def extract_dependencies(doc_path: Path) -> Dict:
    """Extract dependency information from doc metadata"""
    try:
        content = doc_path.read_text(encoding='utf-8')
        metadata, _ = parse_frontmatter(content)
        
        # Extract dependencies
        dependencies = metadata.get("dependencies", [])
        source_of_truth = metadata.get("source_of_truth")
        source_of_truth_type = metadata.get("source_of_truth_type")
        authoritative = metadata.get("authoritative", False)
        auto_update = metadata.get("auto_update", False)
        
        return {
            "doc_path": str(doc_path.relative_to(project_root)),
            "dependencies": dependencies if isinstance(dependencies, list) else [],
            "source_of_truth": source_of_truth,
            "source_of_truth_type": source_of_truth_type,
            "authoritative": authoritative,
            "auto_update": auto_update,
            "metadata": metadata
        }
    except Exception as e:
        return {
            "doc_path": str(doc_path.relative_to(project_root)),
            "error": str(e),
            "dependencies": [],
            "source_of_truth": None,
            "authoritative": False,
            "auto_update": False
        }


def build_dependency_graph() -> Dict:
    """Build graph of doc → source dependencies"""
    print("Scanning documentation files...")
    docs = find_all_docs()
    print(f"Found {len(docs)} documentation files")
    
    # Extract dependencies from all docs
    doc_deps = {}
    source_dependents = defaultdict(list)  # source → [docs that depend on it]
    
    for doc_path in docs:
        dep_info = extract_dependencies(doc_path)
        doc_deps[dep_info["doc_path"]] = dep_info
        
        # Track dependents for each source
        if dep_info.get("source_of_truth"):
            source = dep_info["source_of_truth"]
            source_dependents[source].append(dep_info["doc_path"])
        
        # Track dependents for each dependency
        for dep in dep_info.get("dependencies", []):
            if isinstance(dep, str):
                source_dependents[dep].append(dep_info["doc_path"])
            elif isinstance(dep, dict):
                dep_path = dep.get("path") or dep.get("doc") or str(dep)
                source_dependents[dep_path].append(dep_info["doc_path"])
    
    # Build dependency graph structure
    dependency_graph = {
        "doc_dependencies": {},
        "source_dependents": dict(source_dependents),
        "leading_docs": [],
        "dependent_docs": []
    }
    
    # Organize by source
    for source, dependents in source_dependents.items():
        # Find source doc info if it exists
        source_info = None
        for doc_path, dep_info in doc_deps.items():
            if doc_path == source or dep_info.get("authoritative"):
                source_info = dep_info
                break
        
        dependency_graph["doc_dependencies"][source] = {
            "type": "auto_generated" if source_info and source_info.get("auto_generated") else "authoritative" if source_info and source_info.get("authoritative") else "unknown",
            "source": source,
            "dependents": dependents,
            "count": len(dependents)
        }
    
    # Find leading docs
    for doc_path, dep_info in doc_deps.items():
        if dep_info.get("authoritative"):
            dependency_graph["leading_docs"].append({
                "path": doc_path,
                "source_of_truth": dep_info.get("source_of_truth"),
                "auto_generated": dep_info.get("auto_generated", False)
            })
    
    # Find dependent docs
    for doc_path, dep_info in doc_deps.items():
        if dep_info.get("dependencies") or dep_info.get("source_of_truth"):
            dependency_graph["dependent_docs"].append({
                "path": doc_path,
                "dependencies": dep_info.get("dependencies", []),
                "source_of_truth": dep_info.get("source_of_truth"),
                "auto_update": dep_info.get("auto_update", False)
            })
    
    return dependency_graph, doc_deps


def update_cross_system_yaml(dependency_graph: Dict, dry_run: bool = False) -> bool:
    """Update cross_system_connections.yaml with doc_dependencies section"""
    yaml_path = project_root / "knowledge_architecture" / "NAVIGATION" / "cross_system_connections.yaml"
    
    if not yaml_path.exists():
        print(f"  [ERROR] cross_system_connections.yaml not found: {yaml_path}")
        return False
    
    # Read existing YAML (preserve as text, don't parse)
    content = yaml_path.read_text(encoding='utf-8')
    
    # Build doc_dependencies section
    doc_deps_section = {}
    for source, info in dependency_graph["doc_dependencies"].items():
        doc_deps_section[source] = {
            "type": info["type"],
            "source": info["source"],
            "dependents": info["dependents"],
            "count": info["count"]
        }
    
    # Write updated YAML
    if not dry_run:
        # Check if doc_dependencies section already exists
        if "doc_dependencies:" in content or "# DOC DEPENDENCIES" in content:
            # Replace existing section
            pattern = r'(# DOC DEPENDENCIES.*?)(?=\n---|\n# |\Z)'
            replacement = f"# DOC DEPENDENCIES\n# Last updated: {datetime.now().isoformat()}\n# Total sources: {len(doc_deps_section)}\n# Total dependents: {sum(len(info['dependents']) for info in doc_deps_section.values())}\n\ndoc_dependencies:\n"
            for source, info in sorted(doc_deps_section.items()):
                # Escape source name if needed
                source_key = source.replace('\\', '/')  # Normalize paths
                replacement += f"  \"{source_key}\":\n"
                replacement += f"    type: \"{info['type']}\"\n"
                replacement += f"    source: \"{info['source']}\"\n"
                replacement += f"    dependents:\n"
                for dep in sorted(info['dependents']):
                    dep_normalized = dep.replace('\\', '/')
                    replacement += f"      - \"{dep_normalized}\"\n"
                replacement += f"    count: {info['count']}\n"
            
            updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            # Add new section at end of file
            new_section = f"\n---\n# DOC DEPENDENCIES\n# Last updated: {datetime.now().isoformat()}\n# Total sources: {len(doc_deps_section)}\n# Total dependents: {sum(len(info['dependents']) for info in doc_deps_section.values())}\n\ndoc_dependencies:\n"
            for source, info in sorted(doc_deps_section.items()):
                source_key = source.replace('\\', '/')
                new_section += f"  \"{source_key}\":\n"
                new_section += f"    type: \"{info['type']}\"\n"
                new_section += f"    source: \"{info['source']}\"\n"
                new_section += f"    dependents:\n"
                for dep in sorted(info['dependents']):
                    dep_normalized = dep.replace('\\', '/')
                    new_section += f"      - \"{dep_normalized}\"\n"
                new_section += f"    count: {info['count']}\n"
            
            updated_content = content.rstrip() + "\n" + new_section
        
        yaml_path.write_text(updated_content, encoding='utf-8')
        print(f"  [DONE] Updated cross_system_connections.yaml with doc_dependencies")
        print(f"    Added {len(doc_deps_section)} sources")
        print(f"    Tracking {sum(len(info['dependents']) for info in doc_deps_section.values())} dependents")
    else:
        print(f"  [DRY RUN] Would update cross_system_connections.yaml")
        print(f"    Would add {len(doc_deps_section)} sources")
        print(f"    Would track {sum(len(info['dependents']) for info in doc_deps_section.values())} dependents")
    
    return True


def generate_report(dependency_graph: Dict, doc_deps: Dict) -> str:
    """Generate dependency tracking report"""
    report = []
    report.append("# Document Dependency Tracking Report")
    report.append(f"**Generated:** {datetime.now().isoformat()}")
    report.append("")
    
    report.append("## Leading Docs (Authoritative Sources)")
    report.append("")
    for leading in dependency_graph["leading_docs"]:
        report.append(f"- `{leading['path']}`")
        if leading.get("source_of_truth"):
            report.append(f"  - Source: `{leading['source_of_truth']}`")
        if leading.get("auto_generated"):
            report.append(f"  - Auto-generated: Yes")
    report.append("")
    
    report.append("## Source Dependencies")
    report.append("")
    for source, info in sorted(dependency_graph["doc_dependencies"].items()):
        report.append(f"### `{source}`")
        report.append(f"- Type: {info['type']}")
        report.append(f"- Dependents: {info['count']}")
        if info['dependents']:
            report.append(f"- Dependent docs:")
            for dep in info['dependents'][:10]:  # Show first 10
                report.append(f"  - `{dep}`")
            if len(info['dependents']) > 10:
                report.append(f"  - ... and {len(info['dependents']) - 10} more")
        report.append("")
    
    report.append("## Dependent Docs")
    report.append("")
    report.append(f"Total dependent docs: {len(dependency_graph['dependent_docs'])}")
    report.append("")
    for dep in dependency_graph["dependent_docs"][:20]:  # Show first 20
        report.append(f"- `{dep['path']}`")
        if dep.get("source_of_truth"):
            report.append(f"  - Source: `{dep['source_of_truth']}`")
        if dep.get("dependencies"):
            report.append(f"  - Dependencies: {len(dep['dependencies'])}")
        if dep.get("auto_update"):
            report.append(f"  - Auto-update: Yes")
    report.append("")
    
    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Track document dependencies")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without updating files"
    )
    parser.add_argument(
        "--update-yaml",
        action="store_true",
        help="Update cross_system_connections.yaml"
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Generate report file (optional)"
    )
    
    args = parser.parse_args()
    
    print("Building dependency graph...")
    dependency_graph, doc_deps = build_dependency_graph()
    
    print(f"\nDependency Graph Summary:")
    print(f"  Leading docs: {len(dependency_graph['leading_docs'])}")
    print(f"  Sources: {len(dependency_graph['doc_dependencies'])}")
    print(f"  Dependent docs: {len(dependency_graph['dependent_docs'])}")
    print(f"  Total dependencies: {sum(len(info['dependents']) for info in dependency_graph['doc_dependencies'].values())}")
    
    # Update YAML if requested
    if args.update_yaml:
        update_cross_system_yaml(dependency_graph, dry_run=args.dry_run)
    
    # Generate report if requested
    if args.report:
        report = generate_report(dependency_graph, doc_deps)
        if not args.dry_run:
            args.report.write_text(report, encoding='utf-8')
            print(f"\n[DONE] Report generated: {args.report}")
        else:
            print(f"\n[DRY RUN] Would generate report: {args.report}")
            print("\n" + report[:500] + "...")


if __name__ == "__main__":
    main()

