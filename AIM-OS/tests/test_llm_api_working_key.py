#!/usr/bin/env python3
"""
Test LLM API with Working Key

Tests the full LLM API integration using the working Gemini key.
"""

import os
import sys
from pathlib import Path

# Set working Gemini key
os.environ["GEMINI_API_KEY"] = "AIzaSyCL2QTE7zT8oT6hC_GxM0Nt1p8QDmB5j7w"

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio

async def test_gemini_full_integration():
    """Test Gemini API through full integration"""
    print("=" * 80)
    print("TEST: Gemini API Full Integration")
    print("=" * 80)
    
    try:
        from packages.api_service_registry.llm import get_api_registry
        
        registry = get_api_registry()
        
        # Test through registry call_api method
        print("\n[TEST] Calling Gemini API through registry...")
        result = registry.call_api(
            provider="gemini",
            endpoint="chat-completion",
            method="POST",
            data={
                "messages": [
                    {"role": "user", "content": "Say 'Hello, AIM-OS!' in one sentence."}
                ],
                "model": "gemini-2.5-flash",
                "temperature": 0.7,
                "max_tokens": 100
            },
            integrate_aimos=False  # Skip AIM-OS integration for this test
        )
        
        if result.get("success"):
            data = result.get("data", {})
            print(f"\n[RESULT] Success!")
            print(f"   Content: {data.get('content', '')[:200]}")
            print(f"   Model: {data.get('model')}")
            print(f"   Tokens: {data.get('tokens_used', 0)}")
            print(f"   Provider: {data.get('provider')}")
            print(f"   Key Index: {data.get('key_index', -1)}")
            return True
        else:
            error = result.get("error", "Unknown error")
            print(f"\n[ERROR] {error}")
            return False
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run test"""
    print("\n" + "=" * 80)
    print("LLM API Integration Test - Working Key")
    print("=" * 80)
    
    result = await test_gemini_full_integration()
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if result:
        print("   [SUCCESS] Gemini API integration working!")
        print("\n   Next steps:")
        print("   1. Test with AIM-OS integration enabled")
        print("   2. Fix Cerebras API endpoint")
        print("   3. Test end-to-end with MCP server")
        return 0
    else:
        print("   [FAIL] Gemini API integration failed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

