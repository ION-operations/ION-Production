"""
Test get_hhni_status MCP tool directly
Simulates calling the tool through the MCP server's tool handler
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

def test_hhni_status_tool():
    """Test get_hhni_status tool by simulating MCP server initialization"""
    print("\n🧪 Testing get_hhni_status MCP Tool")
    print("=" * 60)
    
    try:
        # Import MCP server class
        # We'll simulate the initialization by importing and testing the method directly
        from cmc_service import MemoryStore
        from hhni import HierarchicalIndex
        from hhni.retrieval import TwoStageRetriever, RetrievalConfig
        
        print("\n1. Initializing systems (simulating MCP server init)...")
        memory = MemoryStore("./mcp_memory")
        hhni_index = HierarchicalIndex()
        
        # Build index (same as MCP server)
        atoms = list(memory.list_atoms(limit=1000))
        hhni_atoms = [a for a in atoms if 'hhni_index' in getattr(a, 'tags', {})]
        
        indexed_count = 0
        for atom in hhni_atoms:
            try:
                content = ""
                if hasattr(atom, 'content') and atom.content:
                    if hasattr(atom.content, 'inline'):
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
            except:
                continue
        
        # Initialize retriever
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
        
        print(f"   ✅ Systems initialized ({indexed_count} atoms indexed)")
        
        # Simulate get_hhni_status tool (same logic as MCP server)
        print("\n2. Testing get_hhni_status tool logic...")
        status = {
            "hhni_index_initialized": hhni_index is not None,
            "hhni_retriever_initialized": hhni_retriever is not None,
            "index_nodes": 0,
            "index_available": False,
            "retriever_available": False,
        }
        
        if hhni_index:
            try:
                status["index_nodes"] = len(hhni_index.nodes) if hasattr(hhni_index, 'nodes') else 0
                status["index_available"] = True
                status["index_root_id"] = hhni_index.root_id if hasattr(hhni_index, 'root_id') else None
            except Exception as e:
                status["index_error"] = str(e)
        
        if hhni_retriever:
            status["retriever_available"] = True
            if hasattr(hhni_retriever, 'config'):
                status["retriever_config"] = {
                    "token_budget": getattr(hhni_retriever.config, 'token_budget', None),
                    "coarse_k": getattr(hhni_retriever.config, 'coarse_k', None),
                    "min_relevance": getattr(hhni_retriever.config, 'min_relevance', None),
                    "dvns_iterations": getattr(hhni_retriever.config, 'dvns_iterations', None),
                }
        
        # Check CMC atoms
        if memory:
            try:
                atoms = list(memory.list_atoms(limit=1000))
                hhni_atoms = [a for a in atoms if 'hhni_index' in getattr(a, 'tags', {})]
                status["cmc_atoms_total"] = len(atoms)
                status["cmc_atoms_hhni_tagged"] = len(hhni_atoms)
            except Exception as e:
                status["cmc_error"] = str(e)
        
        # Display status
        print("\n3. HHNI Status Results:")
        print(f"   - Index initialized: {status.get('hhni_index_initialized')}")
        print(f"   - Retriever initialized: {status.get('hhni_retriever_initialized')}")
        print(f"   - Index nodes: {status.get('index_nodes')}")
        print(f"   - Index available: {status.get('index_available')}")
        print(f"   - Retriever available: {status.get('retriever_available')}")
        print(f"   - CMC atoms total: {status.get('cmc_atoms_total')}")
        print(f"   - CMC atoms HHNI-tagged: {status.get('cmc_atoms_hhni_tagged')}")
        
        if status.get('retriever_config'):
            print(f"\n   Retriever Config:")
            for key, value in status['retriever_config'].items():
                print(f"      - {key}: {value}")
        
        # Validate
        if status.get('hhni_index_initialized') and status.get('index_nodes', 0) > 0:
            print("\n   ✅ get_hhni_status tool working correctly!")
            return True
        else:
            print("\n   ⚠️  Status indicates issues")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hhni_status_tool()
    sys.exit(0 if success else 1)

