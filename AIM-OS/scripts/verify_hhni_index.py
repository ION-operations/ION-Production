#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify HHNI Index Status

Quick script to verify:
1. CMC atoms with hhni_index tag
2. HHNI index nodes after building
3. Index building process
"""

import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add paths
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))
packages_path = workspace_root / "packages"
sys.path.insert(0, str(packages_path))

try:
    from cmc_service import MemoryStore
    from hhni import HierarchicalIndex
except ImportError as e:
    print(f"ERROR: Failed to import: {e}")
    sys.exit(1)


def main():
    """Verify HHNI index status"""
    print("🔍 Verifying HHNI Index Status")
    print("=" * 60)
    
    # Check CMC atoms
    print("\n1. Checking CMC Atoms...")
    memory = MemoryStore("./mcp_memory")
    atoms = list(memory.list_atoms(limit=1000))
    print(f"   Total atoms in CMC: {len(atoms)}")
    
    hhni_atoms = [a for a in atoms if "hhni_index" in a.tags]
    print(f"   Atoms with hhni_index tag: {len(hhni_atoms)}")
    
    if hhni_atoms:
        print(f"\n   Sample atom tags: {list(hhni_atoms[0].tags.keys())[:5]}")
        print(f"   Sample atom modality: {hhni_atoms[0].modality}")
        print(f"   Sample atom has content: {bool(hhni_atoms[0].content.inline)}")
    
    # Build HHNI index
    print("\n2. Building HHNI Index...")
    hhni_index = HierarchicalIndex()
    
    indexed_count = 0
    for atom in hhni_atoms:
        try:
            content = ""
            if hasattr(atom.content, 'inline') and atom.content.inline:
                content = atom.content.inline
            elif isinstance(atom.content, str):
                content = atom.content
            
            if not content:
                continue
            
            doc_id = f"atom_{atom.id}"
            metadata = {
                "atom_id": atom.id,
                "modality": atom.modality,
                "tags": dict(atom.tags),
            }
            
            hhni_index.index_document(content, doc_id, metadata)
            indexed_count += 1
            
        except Exception as e:
            print(f"   ⚠️  Error indexing atom {atom.id[:8]}...: {e}")
            continue
    
    print(f"   ✅ Indexed {indexed_count} documents")
    print(f"   Total nodes in index: {len(hhni_index)}")
    
    # Check index nodes
    print("\n3. Checking Index Nodes...")
    if len(hhni_index) > 0:
        print(f"   ✅ Index has {len(hhni_index)} nodes")
        print(f"   Root ID: {hhni_index.root_id}")
        
        # Show sample nodes
        sample_nodes = list(hhni_index.nodes.values())[:3]
        for i, node in enumerate(sample_nodes, 1):
            print(f"\n   Node {i}:")
            print(f"      ID: {node.id}")
            print(f"      Level: {node.level}")
            print(f"      Content length: {len(node.content)}")
            print(f"      Summary length: {len(node.summary)}")
            print(f"      Has embeddings: {bool(node.embeddings)}")
    else:
        print("   ❌ Index is empty!")
    
    print("\n" + "=" * 60)
    print("✅ Verification complete!")


if __name__ == "__main__":
    main()

