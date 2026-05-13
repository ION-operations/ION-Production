#!/usr/bin/env python3
"""
Store HHNI Index Metadata to CMC

This script reads HHNI index JSON files and stores their metadata
in CMC for persistent storage and bitemporal tracking.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import CMC client (via MCP tools)
# Note: This script will use MCP tools via HTTP endpoint
# For now, we'll prepare the data structure

IDEAS_INDEX_SUMMARY = Path("knowledge_architecture/AETHER_MEMORY/investigations/HHNI_IDEA_INDEX_SUMMARY.json")
ORGANIZED_FILES_INDEX_SUMMARY = Path("HHNI_FLOATING_FILES_INDEX_SUMMARY.json")

def load_index_summary(file_path: Path) -> Dict[str, Any]:
    """Load HHNI index summary JSON."""
    if not file_path.exists():
        raise FileNotFoundError(f"Index summary not found: {file_path}")
    
    return json.loads(file_path.read_text(encoding="utf-8"))

def create_cmc_metadata(index_summary: Dict[str, Any], index_type: str) -> Dict[str, Any]:
    """Create CMC metadata structure from index summary."""
    return {
        "index_type": index_type,
        "total_files": index_summary.get("total_files_indexed", 0),
        "total_nodes": index_summary.get("total_nodes", 0),
        "indexed_at": datetime.now().isoformat(),
        "source_file": str(index_summary.get("indexed_files", [])[0].get("file_path", "")) if index_summary.get("indexed_files") else "",
        "file_count": len(index_summary.get("indexed_files", [])),
        "agent": "aether"
    }

def create_cmc_content(index_summary: Dict[str, Any], index_type: str) -> str:
    """Create CMC content string from index summary."""
    total_files = index_summary.get("total_files_indexed", 0)
    total_nodes = index_summary.get("total_nodes", 0)
    
    return f"""HHNI Index Summary: {index_type}

Total Files Indexed: {total_files}
Total Nodes Created: {total_nodes:,}
Index Type: {index_type}
Indexed At: {datetime.now().isoformat()}

This index provides semantic search capabilities across {total_files} files
with {total_nodes:,} hierarchical nodes.

Use HHNI semantic search to query this index.
"""

def create_cmc_tags(index_type: str) -> Dict[str, str]:
    """Create CMC tags for index storage."""
    return {
        "type": "hhni_index",
        "index_type": index_type,
        "agent": "aether",
        "system": "hhni",
        "storage": "cmc"
    }

def store_index_to_cmc(index_summary: Dict[str, Any], index_type: str):
    """Store index summary to CMC (prepared for MCP tool call)."""
    metadata = create_cmc_metadata(index_summary, index_type)
    content = create_cmc_content(index_summary, index_type)
    tags = create_cmc_tags(index_type)
    
    print(f"\n[*] Prepared CMC storage for {index_type}:")
    print(f"   Files: {metadata['total_files']}")
    print(f"   Nodes: {metadata['total_nodes']:,}")
    print(f"   Content length: {len(content)} chars")
    print(f"   Tags: {tags}")
    
    # Return structure ready for MCP tool call
    return {
        "content": content,
        "tags": tags,
        "metadata": metadata
    }

def main():
    """Main function to store HHNI indexes to CMC."""
    print("[*] Starting HHNI to CMC Integration...")
    print("=" * 70)
    
    # Load index summaries
    print("\n[>] Loading index summaries...")
    
    try:
        ideas_summary = load_index_summary(IDEAS_INDEX_SUMMARY)
        print(f"   ✅ Loaded idea files index: {ideas_summary.get('total_files_indexed', 0)} files")
    except FileNotFoundError:
        print(f"   ⚠️ Idea files index summary not found: {IDEAS_INDEX_SUMMARY}")
        ideas_summary = None
    
    try:
        organized_summary = load_index_summary(ORGANIZED_FILES_INDEX_SUMMARY)
        print(f"   ✅ Loaded organized files index: {organized_summary.get('total_files', 0)} files")
    except FileNotFoundError:
        print(f"   ⚠️ Organized files index summary not found: {ORGANIZED_FILES_INDEX_SUMMARY}")
        organized_summary = None
    
    # Prepare CMC storage structures
    print("\n[>] Preparing CMC storage structures...")
    
    cmc_data = []
    
    if ideas_summary:
        cmc_data.append(store_index_to_cmc(ideas_summary, "idea_files"))
    
    if organized_summary:
        cmc_data.append(store_index_to_cmc(organized_summary, "organized_files"))
    
    # Print summary
    print("\n" + "=" * 70)
    print("[*] CMC STORAGE PREPARATION COMPLETE")
    print("=" * 70)
    print(f"Prepared {len(cmc_data)} index summaries for CMC storage")
    print("\nNext steps:")
    print("1. Use MCP tool: mcp_lucid-mcp_store_memory")
    print("2. Store each prepared structure to CMC")
    print("3. Verify storage via CMC query")
    
    # Save prepared data for manual MCP tool calls
    output_file = Path("knowledge_architecture/AETHER_MEMORY/investigations/HHNI_CMC_STORAGE_PREPARED.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(cmc_data, indent=2), encoding="utf-8")
    print(f"\n[+] Prepared data saved to: {output_file}")
    
    return cmc_data

if __name__ == "__main__":
    try:
        cmc_data = main()
        print("\n[+] HHNI → CMC integration preparation complete!")
        sys.exit(0)
    except Exception as e:
        print(f"\n[-] Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
