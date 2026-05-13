"""
End-to-End Integration Test for RAG MCP Tools

Tests the complete RAG MCP Tools system from MCP server through RAG middleware
to tool selection and learning engine.

Author: Solo
Date: 2025-10-30
"""

import sys
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from mcp_rag_middleware import RAGMCPMiddleware
    from rag_proxy import MCPRAGProxy
    from learning_engine import LearningEngine, ToolUsageRecord
except ImportError:
    # Fallback imports
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from mcp_rag_middleware import RAGMCPMiddleware
    from rag_proxy import MCPRAGProxy
    from learning_engine import LearningEngine, ToolUsageRecord

def test_middleware_integration():
    """Test RAG middleware with mock MCP tools list"""
    print("=== Testing RAG Middleware Integration ===")
    
    try:
        # Create middleware
        middleware = RAGMCPMiddleware(enable_rag=True)
        
        # Mock all 54 tools (simplified structure)
        all_tools = [
            {"name": "store_memory", "description": "Store information in AIM-OS persistent memory"},
            {"name": "retrieve_memory", "description": "Search and retrieve memories from AIM-OS"},
            {"name": "get_memory_stats", "description": "Get statistics about the AIM-OS memory system"},
            {"name": "create_plan", "description": "Create an execution plan using APOE"},
            {"name": "track_confidence", "description": "Track confidence and provenance using VIF"},
            {"name": "synthesize_knowledge", "description": "Synthesize knowledge using SEG"},
            # ... (would include all 54 tools in real test)
        ]
        
        # Add context
        middleware.add_context("I need to store some memory about user preferences")
        
        # Test filtering
        mock_request = {"params": {}}
        filtered = middleware.filter_tools(all_tools, query="Store memory about user preferences")
        
        print(f"✅ Middleware filtering: {len(all_tools)} → {len(filtered)} tools")
        print(f"   Context reduction: {(1 - len(filtered) / len(all_tools)) * 100:.1f}%")
        
        if filtered:
            print(f"   Top tools: {[t.get('name') for t in filtered[:3]]}")
        
        return True
    except Exception as e:
        print(f"❌ Middleware integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_learning_cycle():
    """Test complete learning cycle"""
    print("\n=== Testing Learning Cycle ===")
    
    try:
        # Initialize components
        proxy = MCPRAGProxy(
            tools_metadata_path="packages/mcp_rag_proxy/tools_metadata.json",
            enable_learning=True,
            learning_db_path="test_rag_learning.db"
        )
        
        if not proxy.enable_learning or not proxy.learning_engine:
            print("⚠️  Learning engine not available, skipping test")
            return False
        
        # Test query
        query = "Store memory about user preferences"
        
        # Select tools
        selections = proxy.select_tools(query, max_tools=5)
        selected_tool_ids = [s.tool_id for s in selections]
        
        print(f"✅ Selected {len(selections)} tools")
        print(f"   Top tool: {selections[0].tool_id if selections else 'None'}")
        
        # Record successful usage
        proxy.record_tool_usage(
            tool_id="store_memory",
            query=query,
            selected_tools=selected_tool_ids,
            success=True,
            quality_score=0.9,
            outcome="Successfully stored user preferences"
        )
        
        # Check learning stats
        stats = proxy.learning_engine.get_learning_stats()
        print(f"✅ Learning stats: {stats['total_records']} records, {stats['overall_success_rate']:.2%} success rate")
        
        # Test adjustment after learning
        adjustment = proxy.learning_engine.get_tool_adjustment("store_memory", query)
        print(f"✅ Learning adjustment for 'store_memory': {adjustment:.3f}x")
        
        # Get tool performance
        perf = proxy.learning_engine.get_tool_performance("store_memory")
        print(f"✅ Tool performance: {perf['total_uses']} uses, {perf['success_rate']:.2%} success rate")
        
        return True
    except Exception as e:
        print(f"❌ Learning cycle test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_end_to_end():
    """Test complete end-to-end flow"""
    print("\n=== Testing End-to-End Flow ===")
    
    try:
        # Initialize middleware
        middleware = RAGMCPMiddleware(enable_rag=True)
        
        # Mock tools list (representative sample)
        all_tools = [
            {"name": f"tool_{i}", "description": f"Tool {i} description"} 
            for i in range(54)
        ]
        
        # Simulate query
        query = "Store memory and retrieve insights"
        middleware.add_context(query)
        
        # Filter tools
        start = time.time()
        filtered = middleware.filter_tools(all_tools, query=query)
        elapsed = (time.time() - start) * 1000
        
        print(f"✅ End-to-end filtering: {len(all_tools)} → {len(filtered)} tools in {elapsed:.2f}ms")
        print(f"   Context reduction: {(1 - len(filtered) / len(all_tools)) * 100:.1f}%")
        
        # Simulate tool usage
        if filtered:
            tool_used = filtered[0].get("name")
            middleware.record_tool_usage(
                tool_name=tool_used,
                success=True,
                quality_score=0.85
            )
            print(f"✅ Recorded usage for: {tool_used}")
        
        # Get stats
        stats = middleware.get_stats()
        print(f"✅ Middleware stats: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests"""
    print("=" * 60)
    print("RAG MCP Tools - End-to-End Integration Test")
    print("=" * 60)
    print()
    
    results = {}
    
    # Test 1: Middleware integration
    results['middleware'] = test_middleware_integration()
    
    # Test 2: Learning cycle
    results['learning'] = test_learning_cycle()
    
    # Test 3: End-to-end flow
    results['end_to_end'] = test_end_to_end()
    
    # Summary
    print("\n" + "=" * 60)
    print("Integration Test Summary")
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

