#!/usr/bin/env python3
"""
Test LLM API MCP Integration - End-to-End

Tests the complete LLM API integration through MCP server with AIM-OS hooks.
"""

import os
import sys
from pathlib import Path

# Set working keys
os.environ["GEMINI_API_KEY"] = "AIzaSyCL2QTE7zT8oT6hC_GxM0Nt1p8QDmB5j7w"
os.environ["GEMINI_API_KEY_1"] = "AIzaSyDiZIEkjqgyJSmQsBYnYuo69fAlkEsgplI"
os.environ["CEREBRAS_API_KEY"] = "csk-prtm28t8d2wttrh5nwj63wpvy9xpejvymw84cm25dtrwhpht"
os.environ["CEREBRAS_API_KEY_1"] = "csk-xv6x26revypveycj6vffvf3yc4fhvx3mxwt9dy6de4xct5ty"

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent))

def test_mcp_integration():
    """Test LLM API through MCP server"""
    print("=" * 80)
    print("LLM API MCP INTEGRATION TEST")
    print("=" * 80)
    
    try:
        from lucid_mcp_server import SimpleMCPServer
        
        # Initialize MCP server
        print("\n[INIT] Initializing MCP server...")
        server = SimpleMCPServer(memory_directory="./test_mcp_memory")
        print("   [OK] MCP server initialized")
        
        # Test Gemini API call
        print("\n" + "=" * 80)
        print("TEST 1: Gemini API Call via MCP")
        print("=" * 80)
        
        gemini_args = {
            "provider": "gemini",
            "endpoint": "chat-completion",
            "method": "POST",
            "data": {
                "messages": [
                    {"role": "user", "content": "Say 'Hello, AIM-OS!' in one sentence."}
                ],
                "model": "gemini-2.5-flash",
                "temperature": 0.7,
                "max_tokens": 100,
                "task_type": "test",
                "agent": "test_agent",
                "thinking_mode": "execution",
                "task_criticality": "ROUTINE"
            },
            "integrate_aimos": True
        }
        
        print("\n[TEST] Calling Gemini API through MCP...")
        gemini_result = server.call_api(gemini_args)
        
        print(f"\n[RESULT] Gemini API Call:")
        print(f"   Success: {gemini_result.get('success', False)}")
        if gemini_result.get('success'):
            data = gemini_result.get('data', {})
            print(f"   Content: {data.get('content', '')[:100]}")
            print(f"   Model: {data.get('model', 'unknown')}")
            print(f"   Tokens: {data.get('tokens_used', 0)}")
            print(f"   Key Index: {data.get('key_index', -1)}")
            
            aimos = gemini_result.get('aimos', {})
            print(f"\n   AIM-OS Integration:")
            print(f"   CMC: {aimos.get('cmc', {}).get('atom_id', 'None')}")
            print(f"   VIF: {aimos.get('vif', {}).get('witness_id', 'None')}")
            print(f"   TCS: {aimos.get('tcs', {}).get('timeline_entry_created', False)}")
        else:
            print(f"   Error: {gemini_result.get('error', 'Unknown error')}")
        
        # Test Cerebras API call
        print("\n" + "=" * 80)
        print("TEST 2: Cerebras API Call via MCP")
        print("=" * 80)
        
        cerebras_args = {
            "provider": "cerebras",
            "endpoint": "chat-completion",
            "method": "POST",
            "data": {
                "messages": [
                    {"role": "user", "content": "Say 'Hello, AIM-OS!' in one sentence."}
                ],
                "model": "llama3.1-8b",
                "temperature": 0.7,
                "max_tokens": 100,
                "task_type": "test",
                "agent": "test_agent",
                "thinking_mode": "execution",
                "task_criticality": "ROUTINE"
            },
            "integrate_aimos": True
        }
        
        print("\n[TEST] Calling Cerebras API through MCP...")
        cerebras_result = server.call_api(cerebras_args)
        
        print(f"\n[RESULT] Cerebras API Call:")
        print(f"   Success: {cerebras_result.get('success', False)}")
        if cerebras_result.get('success'):
            data = cerebras_result.get('data', {})
            print(f"   Content: {data.get('content', '')[:100]}")
            print(f"   Model: {data.get('model', 'unknown')}")
            print(f"   Tokens: {data.get('tokens_used', 0)}")
            print(f"   Key Index: {data.get('key_index', -1)}")
            
            aimos = cerebras_result.get('aimos', {})
            print(f"\n   AIM-OS Integration:")
            print(f"   CMC: {aimos.get('cmc', {}).get('atom_id', 'None')}")
            print(f"   VIF: {aimos.get('vif', {}).get('witness_id', 'None')}")
            print(f"   TCS: {aimos.get('tcs', {}).get('timeline_entry_created', False)}")
        else:
            print(f"   Error: {cerebras_result.get('error', 'Unknown error')}")
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        gemini_success = gemini_result.get('success', False)
        cerebras_success = cerebras_result.get('success', False)
        
        print(f"\n   Gemini: {'[PASS]' if gemini_success else '[FAIL]'}")
        print(f"   Cerebras: {'[PASS]' if cerebras_success else '[FAIL]'}")
        
        if gemini_success and cerebras_success:
            print("\n   [SUCCESS] Both API calls working through MCP!")
            print("\n   Next steps:")
            print("   1. Verify AIM-OS integration (CMC, VIF, TCS)")
            print("   2. Test key rotation scenarios")
            print("   3. Test error handling")
            return 0
        else:
            print("\n   [WARNING] Some tests failed - review errors above")
            return 1
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(test_mcp_integration())

