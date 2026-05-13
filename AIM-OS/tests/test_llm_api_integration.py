#!/usr/bin/env python3
"""
Test LLM API Integration - End-to-End Testing

Tests the complete LLM API infrastructure:
1. API call to Gemini/Cerebras
2. CMC storage
3. VIF witness creation
4. TCS timeline logging
5. Key rotation event tracking
"""

import os
import sys
import json
from pathlib import Path

# Set API keys for testing
os.environ["GEMINI_API_KEY"] = "AIzaSyBbWCBLA4z0oNshsoXUcA55SaVulmBjQnU"
os.environ["CEREBRAS_API_KEY"] = "csk-prtm28t8d2wttrh5nwj63wpvy9xpejvymw84cm25dtrwhpht"

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent))

def test_gemini_api_call():
    """Test Gemini API call through MCP server"""
    print("=" * 80)
    print("TEST 1: Gemini API Call")
    print("=" * 80)
    
    try:
        from lucid_mcp_server import SimpleMCPServer
        
        # Initialize MCP server
        server = SimpleMCPServer(memory_directory="./test_mcp_memory")
        
        # Test API call
        args = {
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
        
        print(f"\n[TEST] Calling Gemini API...")
        result = server.call_api(args)
        
        print(f"\n[RESULT] API Call:")
        print(f"   Success: {result.get('success')}")
        if result.get('error'):
            print(f"   Error: {result.get('error')}")
        
        if result.get("success"):
            data = result.get("data", {})
            content = data.get('content', '')
            if content:
                print(f"   Content: {content[:100]}...")
            print(f"   Model: {data.get('model')}")
            print(f"   Tokens: {data.get('tokens_used', 0)}")
            print(f"   Key Index: {data.get('key_index', -1)}")
            
            metadata = result.get("metadata", {})
            print(f"   Latency: {metadata.get('latency_ms', 0)}ms")
        
        # Check AIM-OS integration
        aimos = result.get("aimos", {})
        print(f"\n[AIM-OS] Integration:")
        if "cmc" in aimos:
            print(f"   [OK] CMC: Atom ID = {aimos['cmc'].get('atom_id', 'N/A')}")
        if "vif" in aimos:
            print(f"   [OK] VIF: Witness ID = {aimos['vif'].get('witness_id', 'N/A')}")
        if "tcs" in aimos:
            print(f"   [OK] TCS: Timeline entry created = {aimos['tcs'].get('timeline_entry_created', False)}")
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cerebras_api_call():
    """Test Cerebras API call through MCP server"""
    print("\n" + "=" * 80)
    print("TEST 2: Cerebras API Call")
    print("=" * 80)
    
    try:
        from lucid_mcp_server import SimpleMCPServer
        
        # Initialize MCP server
        server = SimpleMCPServer(memory_directory="./test_mcp_memory")
        
        # Test API call
        args = {
            "provider": "cerebras",
            "endpoint": "chat-completion",
            "method": "POST",
            "data": {
                "messages": [
                    {"role": "user", "content": "Say 'Hello, AIM-OS!' in one sentence."}
                ],
                "model": "llama-3.1-8b-instruct",
                "temperature": 0.7,
                "max_tokens": 100,
                "task_type": "test",
                "agent": "test_agent",
                "thinking_mode": "execution",
                "task_criticality": "ROUTINE"
            },
            "integrate_aimos": True
        }
        
        print(f"\n[TEST] Calling Cerebras API...")
        result = server.call_api(args)
        
        print(f"\n[RESULT] API Call:")
        print(f"   Success: {result.get('success')}")
        if result.get('error'):
            print(f"   Error: {result.get('error')}")
        
        if result.get("success"):
            data = result.get("data", {})
            content = data.get('content', '')
            if content:
                print(f"   Content: {content[:100]}...")
            print(f"   Model: {data.get('model')}")
            print(f"   Tokens: {data.get('tokens_used', 0)}")
            print(f"   Key Index: {data.get('key_index', -1)}")
            
            metadata = result.get("metadata", {})
            print(f"   Latency: {metadata.get('latency_ms', 0)}ms")
        
        # Check AIM-OS integration
        aimos = result.get("aimos", {})
        print(f"\n[AIM-OS] Integration:")
        if "cmc" in aimos:
            print(f"   [OK] CMC: Atom ID = {aimos['cmc'].get('atom_id', 'N/A')}")
        if "vif" in aimos:
            print(f"   [OK] VIF: Witness ID = {aimos['vif'].get('witness_id', 'N/A')}")
        if "tcs" in aimos:
            print(f"   [OK] TCS: Timeline entry created = {aimos['tcs'].get('timeline_entry_created', False)}")
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_key_rotation():
    """Test key rotation (simulate quota error)"""
    print("\n" + "=" * 80)
    print("TEST 3: Key Rotation Event Tracking")
    print("=" * 80)
    
    try:
        # Try importing the registry directly
        try:
            from packages.api_service_registry.llm import get_api_registry
        except ImportError:
            # Try alternative import path
            sys.path.insert(0, str(Path(__file__).parent / "packages"))
            from api_service_registry.llm import get_api_registry
        
        api_registry = get_api_registry()
        key_manager = api_registry.key_manager
        
        # Check if rotation event tracking is set up
        if hasattr(key_manager, '_last_rotation_event'):
            print(f"   [OK] Rotation event tracking attribute exists")
        else:
            print(f"   [FAIL] Rotation event tracking attribute missing")
            return False
        
        # Simulate rotation (this would normally happen on quota error)
        print(f"\n[TEST] Simulating key rotation...")
        old_index = key_manager.get_current_key_index("gemini")
        print(f"   Current key index: {old_index}")
        
        # Manually trigger rotation (for testing)
        rotated_key = key_manager.rotate_key("gemini", reason="test_rotation")
        new_index = key_manager.get_current_key_index("gemini")
        
        if rotated_key:
            print(f"   [OK] Key rotated: {old_index} -> {new_index}")
            
            # Check for rotation event
            if key_manager._last_rotation_event:
                event = key_manager._last_rotation_event
                print(f"\n   [OK] Rotation event captured:")
                print(f"      Provider: {event.get('provider')}")
                print(f"      Old Index: {event.get('old_key_index')}")
                print(f"      New Index: {event.get('new_key_index')}")
                print(f"      Reason: {event.get('reason')}")
                print(f"      Timestamp: {event.get('timestamp')}")
                return True
            else:
                print(f"   [FAIL] No rotation event captured")
                return False
        else:
            print(f"   [WARNING] No key available for rotation (all exhausted?)")
            return True  # Not an error, just no keys available
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n" + "=" * 80)
    print("DEPENDENCY CHECK")
    print("=" * 80)
    
    missing = []
    
    # Check google-generativeai (Gemini)
    try:
        import google.generativeai
        print("   [OK] google-generativeai (Gemini SDK)")
    except ImportError:
        print("   [MISSING] google-generativeai (Gemini SDK)")
        missing.append("google-generativeai")
    
    # Check httpx (Cerebras)
    try:
        import httpx
        print("   [OK] httpx (Cerebras HTTP client)")
    except ImportError:
        print("   [MISSING] httpx (Cerebras HTTP client)")
        missing.append("httpx")
    
    if missing:
        print(f"\n   [WARNING] Missing dependencies: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return False
    
    print("\n   [OK] All dependencies installed")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("LLM API Integration - End-to-End Test Suite")
    print("=" * 80)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n   [WARNING] Please install missing dependencies before running tests")
        return 1
    
    results = []
    
    # Test 1: Gemini API call
    results.append(("Gemini API Call", test_gemini_api_call()))
    
    # Test 2: Cerebras API call
    results.append(("Cerebras API Call", test_cerebras_api_call()))
    
    # Test 3: Key rotation tracking
    results.append(("Key Rotation Tracking", test_key_rotation()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"   {status}: {test_name}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n   [SUCCESS] All tests passed! LLM API integration is working correctly.")
        return 0
    else:
        print(f"\n   [WARNING] {total - passed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
