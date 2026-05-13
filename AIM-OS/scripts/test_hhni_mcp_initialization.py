"""
Test HHNI initialization in MCP server context
Verifies all fixes from Sev/Atlas are working correctly
"""
import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add paths (same as verify_hhni_index.py)
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))
packages_path = workspace_root / "packages"
sys.path.insert(0, str(packages_path))

try:
    from cmc_service import MemoryStore
    from hhni import HierarchicalIndex
    from hhni.retrieval import TwoStageRetriever, RetrievalConfig
except ImportError as e:
    print(f"ERROR: Failed to import dependencies: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def log(msg: str):
    """Log to stderr only (never stdout - it corrupts JSON-RPC)"""
    print(f"[HHNI-TEST] {msg}", file=sys.stderr, flush=True)

def test_hhni_initialization():
    """Test HHNI initialization similar to MCP server"""
    print("\n🧪 Testing HHNI Initialization (MCP Server Context)")
    print("=" * 60)
    
    # Initialize memory store
    print("\n1. Initializing Memory Store...")
    try:
        memory = MemoryStore("./mcp_memory")
        print(f"   ✅ Memory store initialized")
    except Exception as e:
        print(f"   ❌ ERROR: Failed to initialize memory store: {e}")
        return False
    
    # Check CMC atoms
    print("\n2. Checking CMC Atoms...")
    try:
        atoms = list(memory.list_atoms(limit=1000))
        hhni_atoms = [a for a in atoms if 'hhni_index' in getattr(a, 'tags', {})]
        print(f"   Total atoms: {len(atoms)}")
        print(f"   Atoms with hhni_index tag: {len(hhni_atoms)}")
        
        if not hhni_atoms:
            print("   ⚠️  WARNING: No HHNI-tagged atoms found")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: Failed to list atoms: {e}")
        return False
    
    # Initialize HHNI index
    print("\n3. Initializing HHNI Index...")
    try:
        hhni_index = HierarchicalIndex()
        print(f"   ✅ HHNI index created")
    except Exception as e:
        print(f"   ❌ ERROR: Failed to create HHNI index: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Build index (simulating MCP server _build_hhni_index)
    print("\n4. Building HHNI Index from CMC Atoms...")
    try:
        indexed_count = 0
        failed_count = 0
        
        for atom in hhni_atoms:
            try:
                # Extract content from atom
                content = ""
                if hasattr(atom, 'content') and atom.content:
                    if hasattr(atom.content, 'inline'):
                        content = atom.content.inline
                    elif isinstance(atom.content, str):
                        content = atom.content
                
                if not content:
                    print(f"   ⚠️  WARNING: Atom {atom.id[:8] if hasattr(atom, 'id') else 'unknown'}... has no content, skipping")
                    failed_count += 1
                    continue
                
                # Create document ID from atom ID
                doc_id = f"atom_{atom.id}"
                
                # Create metadata with atom information
                from datetime import datetime
                metadata = {
                    "atom_id": atom.id,
                    "modality": getattr(atom, 'modality', 'text'),
                    "tags": dict(getattr(atom, 'tags', {})),
                    "created_at": getattr(atom, 'created_at', datetime.now()).isoformat() if hasattr(atom, 'created_at') else datetime.now().isoformat()
                }
                
                # Index document in HHNI
                hhni_index.index_document(content, doc_id, metadata)
                indexed_count += 1
                
            except Exception as e:
                print(f"   ⚠️  WARNING: Failed to index atom {atom.id[:8] if hasattr(atom, 'id') else 'unknown'}...: {e}")
                failed_count += 1
                continue
        
        print(f"   ✅ Indexed {indexed_count} atoms, {failed_count} failed")
        
        # Validate index has nodes
        if hasattr(hhni_index, 'nodes'):
            node_count = len(hhni_index.nodes)
            print(f"   ✅ Index validation: {node_count} nodes created")
            if node_count == 0:
                print("   ⚠️  WARNING: HHNI index is empty after building - no nodes created")
                return False
        else:
            print("   ⚠️  WARNING: HHNI index has no 'nodes' attribute")
            return False
        
    except Exception as e:
        print(f"   ❌ ERROR: Failed to build HHNI index: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Initialize retriever
    print("\n5. Initializing TwoStageRetriever...")
    try:
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
        print(f"   ✅ TwoStageRetriever initialized with DVNS physics pipeline")
    except Exception as e:
        print(f"   ❌ ERROR: Failed to initialize retriever: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test retrieval
    print("\n6. Testing Context Retrieval...")
    try:
        result = hhni_retriever.retrieve(
            query="What is AIM-OS?",
            token_budget=2000
        )
        
        if result.selected_items:
            print(f"   ✅ Retrieved {len(result.selected_items)} items")
            print(f"   Total tokens: {result.total_tokens}")
            print(f"   Average relevance: {result.relevance_score:.2f}")
        else:
            print("   ⚠️  WARNING: No items retrieved")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: Failed to retrieve context: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! HHNI initialization working correctly.")
    return True

if __name__ == "__main__":
    success = test_hhni_initialization()
    sys.exit(0 if success else 1)

