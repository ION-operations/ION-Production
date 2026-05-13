"""
Direct test of HHNI initialization in MCP server context
Tests the actual initialization code from lucid_mcp_server.py
"""
import sys
import os
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

def test_mcp_hhni_init():
    """Test HHNI initialization exactly as MCP server does it"""
    print("\n🧪 Testing HHNI Initialization (MCP Server Code Path)")
    print("=" * 60)
    
    try:
        # Import exactly what MCP server imports
        from cmc_service import MemoryStore
        from hhni import HierarchicalIndex, IndexLevel
        from hhni.retrieval import TwoStageRetriever, RetrievalConfig
        
        print("\n1. Initializing Memory Store...")
        memory = MemoryStore("./mcp_memory")
        print("   ✅ Memory store initialized")
        
        print("\n2. Checking CMC Atoms...")
        atoms = list(memory.list_atoms(limit=1000))
        print(f"   Total atoms: {len(atoms)}")
        
        # Filter by hhni_index tag (P0 fix)
        hhni_atoms = [a for a in atoms if 'hhni_index' in getattr(a, 'tags', {})]
        print(f"   Atoms with hhni_index tag: {len(hhni_atoms)}")
        
        if not hhni_atoms:
            print("   ❌ ERROR: No atoms with hhni_index tag found")
            return False
        
        print("\n3. Initializing HHNI Index...")
        hhni_index = HierarchicalIndex()
        print("   ✅ HHNI index created")
        
        print("\n4. Building HHNI Index from CMC Atoms...")
        indexed_count = 0
        failed_count = 0
        
        for atom in hhni_atoms:
            try:
                # Extract content (same as MCP server)
                content = ""
                if hasattr(atom, 'content') and atom.content:
                    if hasattr(atom.content, 'inline'):
                        content = atom.content.inline
                    elif isinstance(atom.content, str):
                        content = atom.content
                
                if not content:
                    failed_count += 1
                    continue
                
                doc_id = f"atom_{atom.id}"
                metadata = {
                    "atom_id": atom.id,
                    "modality": getattr(atom, 'modality', 'text'),
                    "tags": dict(getattr(atom, 'tags', {})),
                }
                if hasattr(atom, 'created_at') and atom.created_at:
                    metadata["created_at"] = atom.created_at.isoformat()
                
                hhni_index.index_document(content, doc_id, metadata)
                indexed_count += 1
                
            except Exception as e:
                print(f"   ⚠️  Error indexing atom {atom.id[:8] if hasattr(atom, 'id') else 'unknown'}...: {e}")
                failed_count += 1
                continue
        
        print(f"   ✅ Indexed {indexed_count} atoms, {failed_count} failed")
        
        # Index validation (P1 fix)
        print("\n5. Validating Index...")
        if hasattr(hhni_index, 'nodes'):
            node_count = len(hhni_index.nodes)
            print(f"   ✅ Index validation: {node_count} nodes created")
            if node_count == 0:
                print("   ❌ ERROR: HHNI index is empty after building")
                return False
        else:
            print("   ❌ ERROR: HHNI index has no 'nodes' attribute")
            return False
        
        print("\n6. Initializing TwoStageRetriever...")
        retrieval_config = RetrievalConfig(
            token_budget=4000,
            coarse_k=100,
            min_relevance=0.3,
            dvns_iterations=50,
            enable_conflict_resolution=True,
            enable_compression=True
        )
        hhni_retriever = TwoStageRetriever(
            hierarchical_index=hhni_index,
            config=retrieval_config
        )
        print("   ✅ TwoStageRetriever initialized with DVNS physics pipeline")
        
        print("\n7. Testing Context Retrieval...")
        retrieval_result = hhni_retriever.retrieve(
            query="What are the core principles of AIM-OS architecture?",
            token_budget=2000,
            target_level=IndexLevel.PARAGRAPH
        )
        
        if retrieval_result.selected_items:
            print(f"   ✅ Retrieved {len(retrieval_result.selected_items)} items")
            print(f"   Total tokens: {retrieval_result.total_tokens}")
            print(f"   Average relevance: {retrieval_result.relevance_score:.2f}")
        else:
            print("   ⚠️  WARNING: No items retrieved")
            return False
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! HHNI initialization working correctly.")
        print(f"   Summary: {indexed_count} atoms indexed, {node_count} nodes created")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mcp_hhni_init()
    sys.exit(0 if success else 1)

