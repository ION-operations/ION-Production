#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test HHNI Retrieval with Indexed Documents

Quick test to verify retrieval works with the indexed documents.
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
    from hhni.retrieval import TwoStageRetriever, RetrievalConfig
except ImportError as e:
    print(f"ERROR: Failed to import: {e}")
    sys.exit(1)


def main():
    """Test HHNI retrieval"""
    print("🧪 Testing HHNI Retrieval")
    print("=" * 60)
    
    # Build index
    print("\n1. Building HHNI Index...")
    memory = MemoryStore("./mcp_memory")
    hhni_index = HierarchicalIndex()
    
    atoms = list(memory.list_atoms(limit=1000))
    hhni_atoms = [a for a in atoms if "hhni_index" in a.tags]
    
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
                "modality": getattr(atom, 'modality', 'text'),
                "tags": dict(getattr(atom, 'tags', {})),
            }
            
            hhni_index.index_document(content, doc_id, metadata)
            indexed_count += 1
        except Exception as e:
            continue
    
    print(f"   ✅ Indexed {indexed_count} documents")
    print(f"   Total nodes: {len(hhni_index)}")
    
    # Initialize retriever
    print("\n2. Initializing Retriever...")
    config = RetrievalConfig(
        token_budget=4000,
        coarse_k=100,
        min_relevance=0.3,
        dvns_iterations=50,
        enable_conflict_resolution=True,
        enable_compression=True
    )
    retriever = TwoStageRetriever(hierarchical_index=hhni_index, config=config)
    print("   ✅ Retriever initialized")
    
    # Test queries
    test_queries = [
        "What is HHNI?",
        "How does HHNI work?",
        "What is CMC?",
        "How does HHNI integrate with CMC?",
    ]
    
    print("\n3. Testing Retrieval...")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        try:
            result = retriever.retrieve(query, token_budget=4000)
            print(f"   Selected Items: {len(result.selected_items)}")
            print(f"   Total Tokens: {result.total_tokens}")
            print(f"   Relevance Score: {result.relevance_score:.3f}")
            
            if result.selected_items:
                print(f"   Top 3 Items:")
                for i, item in enumerate(result.selected_items[:3], 1):
                    print(f"      {i}. Relevance: {item.relevance:.3f}")
                    print(f"         Content preview: {item.content[:80]}...")
            else:
                print("   ⚠️  No items retrieved")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Retrieval test complete!")


if __name__ == "__main__":
    main()

