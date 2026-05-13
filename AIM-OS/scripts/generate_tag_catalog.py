#!/usr/bin/env python3
"""
Generate NL Tag Catalog for a System

Scans all *_TAGGED.py files in a system directory, extracts all NL tags,
and generates a comprehensive markdown catalog organized by category and type.

Usage:
    python scripts/generate_tag_catalog.py packages/vif/ -o knowledge_architecture/systems/vif/NL_TAG_CATALOG.md
    python scripts/generate_tag_catalog.py packages/cmc_service/ -o knowledge_architecture/systems/cmc/NL_TAG_CATALOG.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from packages.nl_tags.universal_registry import UniversalTagRegistry


def generate_catalog(system_path: str, system_name: str) -> str:
    """Generate complete tag catalog markdown for a system
    
    Args:
        system_path: Path to system package (e.g., "packages/vif/")
        system_name: System name (e.g., "VIF")
        
    Returns:
        Complete markdown catalog
    """
    # Scan all tags in system
    registry = UniversalTagRegistry()
    count = registry.scan_codebase(system_path, pattern="*_TAGGED.py")
    
    if count == 0:
        return f"# {system_name} NL Tag Catalog\n\n**No tags found in {system_path}**\n"
    
    # Get all tags for this system
    system_tags = registry.query(system=system_name.upper())
    
    # Organize by category
    by_category = defaultdict(list)
    by_type = defaultdict(list)
    
    for tag_id in system_tags:
        tag_data = registry.get(tag_id)
        if tag_data:
            # Extract category
            parts = tag_id.split("-")
            category = parts[1] if len(parts) > 1 else "UNKNOWN"
            by_category[category].append((tag_id, tag_data))
            
            # Extract type
            tag_type = tag_data.get("kind", "TAG")
            by_type[tag_type].append((tag_id, tag_data))
    
    # Generate markdown
    md = []
    
    # Header
    md.append(f"---")
    md.append(f"id: \"{system_name.lower()}_nl_tag_catalog\"")
    md.append(f"system: \"{system_name.lower()}\"")
    md.append(f"type: \"tag_catalog\"")
    md.append(f"title: \"{system_name} NL Tag Catalog\"")
    md.append(f"description: \"Comprehensive catalog of all NL tags in {system_name}\"")
    md.append(f"generated: \"{datetime.now().isoformat()}\"")
    md.append(f"total_tags: {count}")
    md.append(f"---")
    md.append(f"")
    md.append(f"# {system_name} NL Tag Catalog")
    md.append(f"")
    md.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md.append(f"**Total Tags:** {count}")
    md.append(f"**System:** {system_name}")
    md.append(f"")
    
    # Statistics
    md.append(f"## 📊 Tag Statistics")
    md.append(f"")
    md.append(f"### By Type")
    md.append(f"")
    for tag_type in sorted(by_type.keys()):
        md.append(f"- **{tag_type}:** {len(by_type[tag_type])} tags")
    md.append(f"")
    
    md.append(f"### By Category")
    md.append(f"")
    for category in sorted(by_category.keys()):
        md.append(f"- **{category}:** {len(by_category[category])} tags")
    md.append(f"")
    
    # Tags by category
    md.append(f"---")
    md.append(f"")
    md.append(f"## 📚 Tags by Category")
    md.append(f"")
    
    for category in sorted(by_category.keys()):
        md.append(f"### {system_name}-{category} ({len(by_category[category])} tags)")
        md.append(f"")
        
        for tag_id, tag_data in sorted(by_category[category], key=lambda x: x[0]):
            desc = tag_data.get("description", "")
            syntax = tag_data.get("syntax_ref", "")
            file_path = tag_data.get("file_path", "")
            line_num = tag_data.get("line_number", "")
            
            # Format file reference
            if file_path:
                file_name = Path(file_path).name
                location = f"`{file_name}:{line_num}`"
            else:
                location = ""
            
            md.append(f"**{tag_id}**")
            md.append(f"- **Description:** {desc}")
            md.append(f"- **Syntax:** `{syntax}`")
            if location:
                md.append(f"- **Location:** {location}")
            
            # Show dependencies
            deps = tag_data.get("dependencies", [])
            if deps:
                md.append(f"- **Dependencies:** {', '.join(deps)}")
            
            md.append(f"")
    
    # Tags by type
    md.append(f"---")
    md.append(f"")
    md.append(f"## 🏷️ Tags by Type")
    md.append(f"")
    
    for tag_type in sorted(by_type.keys()):
        md.append(f"### {tag_type} Tags ({len(by_type[tag_type])} tags)")
        md.append(f"")
        
        for tag_id, tag_data in sorted(by_type[tag_type], key=lambda x: x[0])[:20]:  # Show first 20
            desc = tag_data.get("description", "")
            md.append(f"- **{tag_id}:** {desc}")
        
        if len(by_type[tag_type]) > 20:
            md.append(f"- *(... and {len(by_type[tag_type]) - 20} more)*")
        
        md.append(f"")
    
    # Integration points (CONNECT tags)
    connect_tags = by_type.get("CONNECT", [])
    if connect_tags:
        md.append(f"---")
        md.append(f"")
        md.append(f"## 🔗 Cross-System Integrations")
        md.append(f"")
        md.append(f"**Total CONNECT tags:** {len(connect_tags)}")
        md.append(f"")
        
        for tag_id, tag_data in sorted(connect_tags, key=lambda x: x[0]):
            desc = tag_data.get("description", "")
            syntax = tag_data.get("syntax_ref", "")
            md.append(f"**{tag_id}**")
            md.append(f"- {desc}")
            md.append(f"- Integration: `{syntax}`")
            md.append(f"")
    
    # Design decisions (INTENT tags)
    intent_tags = by_type.get("INTENT", [])
    if intent_tags:
        md.append(f"---")
        md.append(f"")
        md.append(f"## 💡 Design Decisions")
        md.append(f"")
        md.append(f"**Total INTENT tags:** {len(intent_tags)}")
        md.append(f"")
        
        for tag_id, tag_data in sorted(intent_tags, key=lambda x: x[0])[:10]:  # Show first 10
            desc = tag_data.get("description", "")
            md.append(f"**{tag_id}**")
            md.append(f"- {desc}")
            md.append(f"")
        
        if len(intent_tags) > 10:
            md.append(f"*(... and {len(intent_tags) - 10} more design decisions documented)*")
            md.append(f"")
    
    # Validations (SPEC tags)
    spec_tags = by_type.get("SPEC", [])
    if spec_tags:
        md.append(f"---")
        md.append(f"")
        md.append(f"## ✅ Schema Validations")
        md.append(f"")
        md.append(f"**Total SPEC tags:** {len(spec_tags)}")
        md.append(f"")
        
        for tag_id, tag_data in sorted(spec_tags, key=lambda x: x[0]):
            desc = tag_data.get("description", "")
            md.append(f"**{tag_id}**")
            md.append(f"- {desc}")
            md.append(f"")
    
    # Usage guide
    md.append(f"---")
    md.append(f"")
    md.append(f"## 📖 Using This Catalog")
    md.append(f"")
    md.append(f"### Finding Tags")
    md.append(f"")
    md.append(f"**By category:** Use the \"Tags by Category\" section")
    md.append(f"**By type:** Use the \"Tags by Type\" section")
    md.append(f"**By function:** Search for function name in descriptions")
    md.append(f"")
    md.append(f"### Understanding Dependencies")
    md.append(f"")
    md.append(f"Each tag lists its dependencies. Follow the chain to understand:")
    md.append(f"- What this tag depends on")
    md.append(f"- What depends on this tag")
    md.append(f"- Complete dependency graph")
    md.append(f"")
    md.append(f"### Code References")
    md.append(f"")
    md.append(f"Each tag shows its location in code:")
    md.append(f"- File name")
    md.append(f"- Line number")
    md.append(f"- Jump to source easily")
    md.append(f"")
    
    # Footer
    md.append(f"---")
    md.append(f"")
    md.append(f"*Generated by: Tag Catalog Generator*")
    md.append(f"*Date: {datetime.now().strftime('%Y-%m-%d')}*")
    md.append(f"*Source: {system_path}*")
    md.append(f"*Total Tags: {count}*")
    
    return "\n".join(md)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Generate NL tag catalog for a system")
    parser.add_argument("system_path", help="Path to system package (e.g., packages/vif/)")
    parser.add_argument("-o", "--output", help="Output file path", required=True)
    parser.add_argument("-s", "--system-name", help="System name (e.g., VIF)")
    
    args = parser.parse_args()
    
    # Determine system name
    system_name = args.system_name
    if not system_name:
        # Extract from path
        path = Path(args.system_path)
        system_name = path.name if path.name != "cmc_service" else "CMC"
        system_name = system_name.upper()
    
    print(f"Generating tag catalog for {system_name}...")
    print(f"Scanning: {args.system_path}")
    
    # Generate catalog
    catalog = generate_catalog(args.system_path, system_name)
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(catalog)
    
    print(f"[OK] Catalog written to: {output_path}")
    
    # Show statistics
    lines = catalog.count('\n')
    tags = catalog.count('**' + system_name)
    
    print(f"  Lines: {lines}")
    print(f"  Tags documented: {tags // 2}")  # Each tag has 2 ** markers
    print(f"")
    print(f"Catalog generation complete!")


if __name__ == "__main__":
    main()

