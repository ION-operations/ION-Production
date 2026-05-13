"""
Test script for RAG MCP Proxy Phase 1 implementation

Tests the new sentence-transformers + FAISS embedding system.
Validates performance, accuracy, and context reduction goals.

Author: Solo
Date: 2025-10-30
"""

import time
import sys
from pathlib import Path

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from mcp_rag_proxy.rag_proxy import MCPRAGProxy
    from mcp_rag_proxy.embedding_generator import EmbeddingGenerator, extract_tool_metadata_from_json, ToolEmbeddingInput
    from mcp_rag_proxy.vector_index import VectorIndex
except ImportError:
    # Fallback to direct imports if package structure different
    from rag_proxy import MCPRAGProxy
    from embedding_generator import EmbeddingGenerator, extract_tool_metadata_from_json, ToolEmbeddingInput
    from vector_index import VectorIndex

def test_embedding_generation():
    """Test embedding generation"""
    print("=== Testing Embedding Generation ===")
    
    try:
        generator = EmbeddingGenerator()
        print(f"✅ Model loaded: {generator.model_name}")
        print(f"✅ Embedding dimension: {generator.get_embedding_dimension()}")
        
        # Test single embedding
        test_tool = ToolEmbeddingInput(
            tool_id="test_tool",
            name="store_memory",
            description="Store information in CMC",
            category="core_aimos",
            tags=["memory", "storage"],
            context_keywords=["store", "save", "memory"]
        )
        
        start = time.time()
        embedding = generator.generate_embedding(test_tool)
        elapsed = (time.time() - start) * 1000
        
        print(f"✅ Single embedding generated: {len(embedding)} dimensions in {elapsed:.2f}ms")
        
        # Test batch embedding
        metadata_path = Path(__file__).parent / "tools_metadata.json"
        tools = extract_tool_metadata_from_json(str(metadata_path))
        if tools:
            start = time.time()
            embeddings = generator.generate_embeddings_batch(tools[:10])  # Test with 10 tools
            elapsed = (time.time() - start) * 1000
            print(f"✅ Batch embedding ({len(embeddings)} tools): {elapsed:.2f}ms ({elapsed/len(embeddings):.2f}ms per tool)")
        
        return True
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vector_index():
    """Test FAISS vector index"""
    print("\n=== Testing Vector Index ===")
    
    try:
        # Load tools
        metadata_path = Path(__file__).parent / "tools_metadata.json"
        tools = extract_tool_metadata_from_json(str(metadata_path))
        if not tools:
            print("⚠️  No tools found in metadata")
            return False
        
        print(f"✅ Loaded {len(tools)} tools from metadata")
        
        # Build index
        generator = EmbeddingGenerator()
        index = VectorIndex(embedding_dim=generator.get_embedding_dimension())
        
        print("Building FAISS index...")
        start = time.time()
        index.build_index(tools, generator=generator)
        elapsed = (time.time() - start) * 1000
        print(f"✅ Index built: {index.size()} tools in {elapsed:.2f}ms")
        
        # Test search
        test_query = "Store memory about user preferences"
        query_embedding = generator.generate_embedding(
            ToolEmbeddingInput(
                tool_id="query",
                name="query",
                description=test_query,
                category="query",
                tags=[],
                context_keywords=[]
            )
        )
        
        start = time.time()
        results = index.search(query_embedding, k=10)
        elapsed = (time.time() - start) * 1000
        
        print(f"✅ Search completed: {len(results)} results in {elapsed:.2f}ms")
        print(f"   Top 3 results:")
        for i, (tool_id, score) in enumerate(results[:3]):
            tool = index.get_tool_by_id(tool_id)
            print(f"   {i+1}. {tool_id}: {score:.4f} ({tool.name if tool else 'N/A'})")
        
        return True
    except Exception as e:
        print(f"❌ Vector index test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_selection():
    """Test tool selection with various queries"""
    print("\n=== Testing Tool Selection ===")
    
    test_queries = [
        ("Store memory about user preferences", "store_memory"),
        ("Get consciousness metrics", "get_consciousness_metrics"),
        ("Create execution plan", "create_plan"),
        ("Track confidence for task", "track_confidence"),
        ("Retrieve memories", "retrieve_memory"),
        ("Start autonomous operation", "start_autonomous_operation"),
    ]
    
    try:
        metadata_path = Path(__file__).parent / "tools_metadata.json"
        proxy = MCPRAGProxy(
            tools_metadata_path=str(metadata_path),
            max_tools=10,
            use_new_embeddings=True
        )
        
        print(f"✅ Proxy initialized: {proxy.vector_index.size() if proxy.use_new_embeddings else len(proxy.tools_metadata)} tools")
        
        correct_selections = 0
        total_time = 0
        
        for query, expected_tool in test_queries:
            start = time.time()
            selections = proxy.select_tools(query, consciousness_state="neutral", max_tools=5)
            elapsed = (time.time() - start) * 1000
            total_time += elapsed
            
            # Check if expected tool is in top 3
            top_tools = [s.tool_id for s in selections[:3]]
            is_correct = expected_tool in top_tools
            
            if is_correct:
                correct_selections += 1
            
            status = "✅" if is_correct else "⚠️"
            print(f"{status} Query: '{query}'")
            if selections:
                print(f"   Top tool: {selections[0].tool_id} (score: {selections[0].final_score:.4f})")
            else:
                print(f"   Top tool: None (no selections returned)")
            print(f"   Expected: {expected_tool}")
            print(f"   Time: {elapsed:.2f}ms")
            print(f"   Selected: {len(selections)} tools")
            
            # Calculate context reduction
            total_tools = proxy.vector_index.size() if proxy.use_new_embeddings else len(proxy.tools_metadata)
            reduction = (1 - len(selections) / total_tools) * 100
            print(f"   Context reduction: {reduction:.1f}%")
            print()
        
        accuracy = (correct_selections / len(test_queries)) * 100
        avg_time = total_time / len(test_queries)
        
        print(f"✅ Selection Accuracy: {accuracy:.1f}% ({correct_selections}/{len(test_queries)})")
        print(f"✅ Average Selection Time: {avg_time:.2f}ms")
        
        return accuracy >= 80, avg_time < 100
    except Exception as e:
        print(f"❌ Tool selection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, False

def test_performance():
    """Test performance benchmarks"""
    print("\n=== Performance Benchmarks ===")
    
    try:
        metadata_path = Path(__file__).parent / "tools_metadata.json"
        proxy = MCPRAGProxy(
            tools_metadata_path=str(metadata_path),
            max_tools=10,
            use_new_embeddings=True
        )
        
        # Test query
        query = "Store memory and retrieve insights"
        
        # Warm up
        proxy.select_tools(query, max_tools=5)
        
        # Benchmark
        times = []
        for _ in range(10):
            start = time.time()
            proxy.select_tools(query, max_tools=10)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"✅ Average time: {avg_time:.2f}ms")
        print(f"✅ Min time: {min_time:.2f}ms")
        print(f"✅ Max time: {max_time:.2f}ms")
        
        target_met = avg_time < 100
        print(f"{'✅' if target_met else '❌'} Performance target (<100ms): {'MET' if target_met else 'NOT MET'}")
        
        return target_met
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_context_reduction():
    """Test context reduction goal (80%)"""
    print("\n=== Context Reduction Test ===")
    
    try:
        metadata_path = Path(__file__).parent / "tools_metadata.json"
        proxy = MCPRAGProxy(
            tools_metadata_path=str(metadata_path),
            max_tools=10,
            use_new_embeddings=True
        )
        
        total_tools = proxy.vector_index.size() if proxy.use_new_embeddings else len(proxy.tools_metadata)
        selected_tools = 10  # max_tools
        
        reduction = (1 - selected_tools / total_tools) * 100
        
        print(f"✅ Total tools: {total_tools}")
        print(f"✅ Selected tools: {selected_tools}")
        print(f"✅ Context reduction: {reduction:.1f}%")
        
        target_met = reduction >= 80
        print(f"{'✅' if target_met else '❌'} Context reduction target (≥80%): {'MET' if target_met else 'NOT MET'}")
        
        return target_met
    except Exception as e:
        print(f"❌ Context reduction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("RAG MCP Proxy Phase 1 - Testing & Validation")
    print("=" * 60)
    print()
    
    results = {}
    
    # Test 1: Embedding generation
    results['embedding'] = test_embedding_generation()
    
    # Test 2: Vector index
    results['index'] = test_vector_index()
    
    # Test 3: Tool selection
    results['selection_accuracy'], results['selection_performance'] = test_tool_selection()
    
    # Test 4: Performance
    results['performance'] = test_performance()
    
    # Test 5: Context reduction
    results['context_reduction'] = test_context_reduction()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    print(f"\n{'✅ ALL TESTS PASSED' if all_passed else '⚠️ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

