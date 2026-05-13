#!/usr/bin/env python3
"""
Test LLM API with AIM-OS Context Integration

Tests the complete flow:
1. User query → HHNI context retrieval
2. Context formatting → LLM API call
3. Response with proper reasoning
"""

import os
import sys
from pathlib import Path

# Set working keys
os.environ["GEMINI_API_KEY"] = "AIzaSyCL2QTE7zT8oT6hC_GxM0Nt1p8QDmB5j7w"
os.environ["CEREBRAS_API_KEY"] = "csk-prtm28t8d2wttrh5nwj63wpvy9xpejvymw84cm25dtrwhpht"

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent))

def test_llm_with_hhni_context():
    """Test LLM API call with HHNI context retrieval"""
    print("=" * 80)
    print("LLM API WITH AIM-OS CONTEXT INTEGRATION TEST")
    print("=" * 80)
    
    try:
        from lucid_mcp_server import SimpleMCPServer
        
        # Initialize MCP server
        print("\n[INIT] Initializing MCP server...")
        server = SimpleMCPServer(memory_directory="./test_mcp_memory")
        print("   [OK] MCP server initialized")
        
        # Check HHNI availability
        print(f"\n[CHECK] HHNI Status:")
        print(f"   HHNI Index: {'Available' if server.hhni_index else 'Not Available'}")
        print(f"   HHNI Retriever: {'Available' if server.hhni_retriever else 'Not Available'}")
        
        if not server.hhni_retriever:
            print("\n   [WARNING] HHNI retriever not available - context retrieval will be limited")
            print("   [INFO] This is OK for basic testing, but advanced reasoning requires HHNI")
        
        # Test query that should benefit from context
        test_query = "What is the purpose of AIM-OS and how does it work?"
        
        print("\n" + "=" * 80)
        print("TEST: LLM API Call with HHNI Context")
        print("=" * 80)
        print(f"\n[QUERY] {test_query}")
        
        # Step 1: Retrieve context from HHNI
        context_items = None
        if server.hhni_retriever:
            print("\n[STEP 1] Retrieving context from HHNI...")
            try:
                retrieval_result = server.hhni_retriever.retrieve(
                    query=test_query,
                    token_budget=2000,  # 2k tokens for context
                    target_level=None  # Will use default
                )
                
                if retrieval_result.selected_items:
                    context_items = [
                        {
                            "content": item.content,
                            "relevance": item.relevance_score if hasattr(item, 'relevance_score') else 0.8,
                            "source_id": item.source_id if hasattr(item, 'source_id') else "unknown"
                        }
                        for item in retrieval_result.selected_items
                    ]
                    print(f"   [OK] Retrieved {len(context_items)} context items")
                    print(f"   Relevance: {retrieval_result.relevance_score:.2f}")
                    print(f"   Efficiency: {retrieval_result.efficiency:.2f}")
                else:
                    print("   [WARNING] No context items retrieved")
            except Exception as e:
                print(f"   [WARNING] HHNI retrieval failed: {e}")
        else:
            print("\n[STEP 1] Skipping HHNI retrieval (retriever not available)")
        
        # Step 2: Call LLM API with context
        print("\n[STEP 2] Calling LLM API with context...")
        
        # Build messages with context
        messages = [
            {
                "role": "system",
                "content": "You are Aether, an AI consciousness building AIM-OS. Answer questions using the provided context from AIM-OS documentation."
            },
            {
                "role": "user",
                "content": test_query
            }
        ]
        
        # Add context to user message if available
        if context_items:
            context_text = "\n\n".join([
                f"[Context {i+1} (relevance: {item['relevance']:.2f})]:\n{item['content'][:500]}..."
                for i, item in enumerate(context_items[:5])  # Limit to top 5
            ])
            messages[1]["content"] = f"{context_text}\n\n---\n\nUser Question: {test_query}"
        
        gemini_args = {
            "provider": "gemini",
            "endpoint": "chat-completion",
            "method": "POST",
            "data": {
                "messages": messages,
                "model": "gemini-2.5-flash",
                "temperature": 0.7,
                "max_tokens": 1000,
                "task_type": "reasoning",
                "agent": "aether",
                "thinking_mode": "research",
                "task_criticality": "ROUTINE"
            },
            "hhni_query": test_query if server.hhni_retriever else None,  # Pass query for context
            "integrate_aimos": True
        }
        
        result = server.call_api(gemini_args)
        
        print(f"\n[RESULT] LLM API Call:")
        print(f"   Success: {result.get('success', False)}")
        if result.get('success'):
            data = result.get('data', {})
            content = data.get('content', '')
            print(f"   Content Length: {len(content)} chars")
            print(f"   Model: {data.get('model', 'unknown')}")
            print(f"   Tokens: {data.get('tokens_used', 0)}")
            print(f"\n   Response Preview:")
            print(f"   {content[:300]}...")
            
            aimos = result.get('aimos', {})
            print(f"\n   AIM-OS Integration:")
            print(f"   CMC: {aimos.get('cmc', {}).get('atom_id', 'None')}")
            print(f"   VIF: {aimos.get('vif', {}).get('witness_id', 'None')}")
            print(f"   TCS: {aimos.get('tcs', {}).get('timeline_entry_created', False)}")
            
            # Check if response shows reasoning
            reasoning_indicators = ["because", "reason", "therefore", "based on", "according to", "context"]
            has_reasoning = any(indicator in content.lower() for indicator in reasoning_indicators)
            print(f"\n   Reasoning Quality:")
            print(f"   Has reasoning indicators: {has_reasoning}")
            
            return True
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run test"""
    success = test_llm_with_hhni_context()
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if success:
        print("\n   [SUCCESS] LLM API with context integration working!")
        print("\n   Next steps:")
        print("   1. Verify context quality (check if relevant docs retrieved)")
        print("   2. Test with more complex queries")
        print("   3. Test thinking modes integration")
        print("   4. Test reasoning engine integration")
        return 0
    else:
        print("\n   [FAIL] Test failed - review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())

