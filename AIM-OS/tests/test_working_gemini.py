#!/usr/bin/env python3
"""
Test Working Gemini Key - Direct Client Test

Tests the working Gemini key directly through the client.
"""

import os
import sys
import asyncio
from pathlib import Path

# Set working Gemini key
os.environ["GEMINI_API_KEY"] = "AIzaSyCL2QTE7zT8oT6hC_GxM0Nt1p8QDmB5j7w"

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_working_gemini():
    """Test working Gemini key"""
    print("=" * 80)
    print("TEST: Working Gemini Key")
    print("=" * 80)
    
    try:
        from packages.api_service_registry.llm import get_api_registry
        
        registry = get_api_registry()
        gemini_client = registry.get_client("gemini")
        
        if not gemini_client:
            print("[FAIL] Gemini client not found")
            return False
        
        # Check key loading
        key_manager = registry.key_manager
        gemini_keys = key_manager.keys.get("gemini", [])
        print(f"\n[INFO] Gemini keys loaded: {len(gemini_keys)}")
        if gemini_keys:
            print(f"[INFO] First key (first 30 chars): {gemini_keys[0][:30]}...")
        
        # Test API call
        print("\n[TEST] Calling Gemini API...")
        result = await gemini_client.chat(
            messages=[{"role": "user", "content": "Say 'Hello, AIM-OS!' in one sentence."}],
            model="gemini-2.5-flash",
            temperature=0.7,
            max_tokens=100
        )
        
        print(f"\n[RESULT] Success!")
        print(f"   Content: {result.get('content', '')[:200]}")
        print(f"   Model: {result.get('model')}")
        print(f"   Tokens: {result.get('tokens_used', 0)}")
        print(f"   Provider: {result.get('provider')}")
        print(f"   Key Index: {result.get('key_index', -1)}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run test"""
    result = await test_working_gemini()
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if result:
        print("   [SUCCESS] Gemini API working with key 4!")
        print("\n   Working Key:")
        print("   AIzaSyCL2QTE7zT8oT6hC_GxM0Nt1p8QDmB5j7w")
        print("\n   Next steps:")
        print("   1. Update test scripts to use this key")
        print("   2. Fix Cerebras API endpoint (all keys failed)")
        print("   3. Test full MCP integration")
        return 0
    else:
        print("   [FAIL] Gemini API test failed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

