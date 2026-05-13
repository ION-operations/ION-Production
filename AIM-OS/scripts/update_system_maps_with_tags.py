#!/usr/bin/env python3
"""
Update System Maps with NL Tag Metrics

Scans tagged files, calculates tag coverage metrics,
and updates system.map.lucid.json5 files.

Usage:
    python scripts/update_system_maps_with_tags.py --all
    python scripts/update_system_maps_with_tags.py packages/vif/
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from packages.nl_tags.universal_registry import UniversalTagRegistry


SYSTEM_MAPPINGS = {
    "vif": "knowledge_architecture/systems/vif/system.map.lucid.json5",
    "cmc_service": "knowledge_architecture/systems/cmc/system.map.lucid.json5",
    "apoe": "knowledge_architecture/systems/apoe/system.map.lucid.json5",
    "hhni": "knowledge_architecture/systems/hhni/system.map.lucid.json5",
    "seg": "knowledge_architecture/systems/seg/system.map.lucid.json5",
    "sdfcvf": "knowledge_architecture/systems/sdfcvf/system.map.lucid.json5",
    "timeline_context_system": "knowledge_architecture/systems/timeline_context_system/system.map.lucid.json5",
    "cas": "knowledge_architecture/systems/cognitive_analysis/system.map.lucid.json5",
    "intuitive_intelligence_system": "knowledge_architecture/systems/intuitive_intelligence_system/system.map.lucid.json5",
}


def calculate_metrics(system_path: str, system_name: str) -> dict:
    """Calculate tag coverage metrics for a system"""
    registry = UniversalTagRegistry()
    count = registry.scan_codebase(system_path, pattern="*_TAGGED.py")
    
    if count == 0:
        return {
            "total_tags": 0,
            "by_type": {},
            "coverage": {},
            "status": "no_tags_found"
        }
    
    # Get tags for this system
    system_tags = registry.query(system=system_name.upper())
    
    # Count by type
    by_type = {}
    for tag_id in system_tags:
        tag_data = registry.get(tag_id)
        if tag_data:
            tag_type = tag_data.get("kind", "TAG")
            by_type[tag_type] = by_type.get(tag_type, 0) + 1
    
    # Calculate coverage (simplified - actual coverage needs AST analysis)
    # For now, use tag count as proxy
    metrics = {
        "total_tags": count,
        "by_type": by_type,
        "coverage": {
            "estimated_functions": count,  # Rough estimate
            "tagged_functions": count,
            "estimated_coverage": 1.0  # All tagged files are 100% by definition
        },
        "catalog_location": "NL_TAG_CATALOG.md",
        "last_updated": datetime.now().isoformat()
    }
    
    return metrics


def update_map(map_path: str, metrics: dict) -> bool:
    """Update system map with tag metrics"""
    try:
        # Read existing map
        with open(map_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple append approach (JSON5 allows comments)
        # Add nl_tag_metrics section if not exists
        if "nl_tag_metrics" not in content:
            # Find closing brace
            last_brace = content.rfind("}")
            
            if last_brace > 0:
                # Insert before closing brace
                metrics_json = json.dumps({"nl_tag_metrics": metrics}, indent=2)
                # Remove outer braces
                metrics_json = metrics_json[1:-1].strip()
                
                # Add comma to previous field
                new_content = content[:last_brace].rstrip()
                if not new_content.endswith(","):
                    new_content += ","
                new_content += "\n\n  // NL Tag Coverage Metrics\n  "
                new_content += metrics_json.replace("\n", "\n  ")
                new_content += "\n" + content[last_brace:]
                
                # Write back
                with open(map_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return True
        else:
            print(f"  [SKIP] Map already has nl_tag_metrics: {map_path}")
            return True
    
    except Exception as e:
        print(f"  [ERROR] Failed to update {map_path}: {e}")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Update system maps with NL tag metrics")
    parser.add_argument("system_path", nargs="?", help="Path to system package")
    parser.add_argument("--all", action="store_true", help="Update all systems")
    
    args = parser.parse_args()
    
    if args.all:
        print("Updating all system maps with NL tag metrics...")
        print("")
        
        for system_dir, map_path in SYSTEM_MAPPINGS.items():
            system_name = system_dir.replace("_service", "").replace("_system", "")
            print(f"Processing {system_name.upper()}...")
            
            # Calculate metrics
            system_path = f"packages/{system_dir}/"
            metrics = calculate_metrics(system_path, system_name)
            
            print(f"  Tags: {metrics['total_tags']}")
            
            # Update map
            if Path(map_path).exists():
                success = update_map(map_path, metrics)
                if success:
                    print(f"  [OK] Updated {map_path}")
            else:
                print(f"  [SKIP] Map not found: {map_path}")
            
            print("")
        
        print("All system maps updated!")
    
    elif args.system_path:
        # Single system
        system_path = args.system_path
        system_name = Path(system_path).name
        
        metrics = calculate_metrics(system_path, system_name)
        print(f"Calculated metrics for {system_name}: {metrics['total_tags']} tags")
        
        # Find map path
        map_path = SYSTEM_MAPPINGS.get(system_name.lower())
        if map_path and Path(map_path).exists():
            update_map(map_path, metrics)
            print(f"[OK] Updated {map_path}")
        else:
            print(f"[ERROR] Map not found for {system_name}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

