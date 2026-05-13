#!/usr/bin/env python3
"""
Simple LLM API Test - Direct Client Testing

Tests LLM clients directly without MCP server to isolate issues.
"""

import os
import sys
from pathlib import Path

# Set API keys BEFORE importing anything
os.environ["GEMINI_API_KEY"] = "AIzaSyBbWCBLA4z0oNshsoXUcA55SaVulmBjQnU"
os.environ["CEREBRAS_API_KEY"] = "csk-prtm28t8d2wttrh5nwj63wpvy9xpejvymw84cm25dtrwhpht"

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio

async def test_gemini_direct():
    """Test Gemini client directly"""
    print("=" * 80)
    print("TEST: Gemini Client Direct")
    print("=" * 80)
    
    try:
        from packages.api_service_registry.llm import get_api_registry
        
        registry = get_api_registry()
        gemini_client = registry.get_client("gemini")
        
        if not gemini_client:
            print("[FAIL] Gemini client not found")
            return False
        
        # Check if keys are loaded
        key_manager = registry.key_manager
        gemini_keys = key_manager.keys.get("gemini", [])
        print(f"\n[INFO] Gemini keys loaded: {len(gemini_keys)}")
        if gemini_keys:
            print(f"[INFO] First key (first 20 chars): {gemini_keys[0][:20]}...")
        
        if not gemini_keys:
            print("[FAIL] No Gemini keys loaded")
            return False
        
        # Test API call
        print("\n[TEST] Calling Gemini API...")
        result = await gemini_client.chat(
            messages=[{"role": "user", "content": "Say 'Hello, AIM-OS!' in one sentence."}],
            model="gemini-2.5-flash",
            temperature=0.7,
            max_tokens=100
        )
        
        print(f"\n[RESULT] Success!")
        print(f"   Content: {result.get('content', '')[:100]}...")
        print(f"   Model: {result.get('model')}")
        print(f"   Tokens: {result.get('tokens_used', 0)}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_cerebras_direct():
    """Test Cerebras client directly"""
    print("\n" + "=" * 80)
    print("TEST: Cerebras Client Direct")
    print("=" * 80)
    
    try:
        from packages.api_service_registry.llm import get_api_registry
        
        registry = get_api_registry()
        cerebras_client = registry.get_client("cerebras")
        
        if not cerebras_client:
            print("[FAIL] Cerebras client not found")
            return False
        
        # Check if keys are loaded
        key_manager = registry.key_manager
        cerebras_keys = key_manager.keys.get("cerebras", [])
        print(f"\n[INFO] Cerebras keys loaded: {len(cerebras_keys)}")
        if cerebras_keys:
            print(f"[INFO] First key (first 20 chars): {cerebras_keys[0][:20]}...")
        
        if not cerebras_keys:
            print("[FAIL] No Cerebras keys loaded")
            return False
        
        # Test API call
        print("\n[TEST] Calling Cerebras API...")
        result = await cerebras_client.chat(
            messages=[{"role": "user", "content": "Say 'Hello, AIM-OS!' in one sentence."}],
            model="llama-3.1-8b-instruct",
            temperature=0.7,
            max_tokens=100
        )
        
        print(f"\n[RESULT] Success!")
        print(f"   Content: {result.get('content', '')[:100]}...")
        print(f"   Model: {result.get('model')}")
        print(f"   Tokens: {result.get('tokens_used', 0)}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("LLM API Direct Client Test")
    print("=" * 80)
    
    results = []
    
    # Test Gemini
    results.append(("Gemini Direct", await test_gemini_direct()))
    
    # Test Cerebras
    results.append(("Cerebras Direct", await test_cerebras_direct()))
    
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
        print("\n   [SUCCESS] All direct client tests passed!")
        return 0
    else:
        print(f"\n   [WARNING] {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

