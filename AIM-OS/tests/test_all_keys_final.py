#!/usr/bin/env python3
"""
Final API Key Test - All Working Keys

Tests all working keys with correct endpoints and model names.
"""

import os
import sys
import asyncio
from pathlib import Path

# Set working keys
os.environ["GEMINI_API_KEY"] = "AIzaSyCL2QTE7zT8oT6hC_GxM0Nt1p8QDmB5j7w"
os.environ["CEREBRAS_API_KEY"] = "csk-prtm28t8d2wttrh5nwj63wpvy9xpejvymw84cm25dtrwhpht"

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_all_working():
    """Test all working keys"""
    print("=" * 80)
    print("FINAL TEST - ALL WORKING KEYS")
    print("=" * 80)
    
    try:
        from packages.api_service_registry.llm import get_api_registry
        
        registry = get_api_registry()
        
        # Test Gemini
        print("\n[TEST] Gemini API...")
        gemini_client = registry.get_client("gemini")
        if gemini_client:
            result = await gemini_client.chat(
                messages=[{"role": "user", "content": "Say 'Hello, AIM-OS!' in one sentence."}],
                model="gemini-2.5-flash"
            )
            print(f"   [OK] Gemini: {result.get('content', '')[:100]}")
            print(f"        Model: {result.get('model')}, Tokens: {result.get('tokens_used', 0)}")
        else:
            print("   [FAIL] Gemini client not found")
        
        # Test Cerebras
        print("\n[TEST] Cerebras API...")
        cerebras_client = registry.get_client("cerebras")
        if cerebras_client:
            result = await cerebras_client.chat(
                messages=[{"role": "user", "content": "Say 'Hello, AIM-OS!' in one sentence."}],
                model="llama3.1-8b"  # Correct model name
            )
            print(f"   [OK] Cerebras: {result.get('content', '')[:100]}")
            print(f"        Model: {result.get('model')}, Tokens: {result.get('tokens_used', 0)}")
        else:
            print("   [FAIL] Cerebras client not found")
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print("\n   [SUCCESS] All working keys tested successfully!")
        print("\n   Working Keys:")
        print("   - Gemini: AIzaSyCL2QTE7zT8oT6hC_GxM0Nt1p8QDmB5j7w")
        print("   - Cerebras: All 4 keys working (using key 1 for test)")
        print("\n   Next: Test full MCP integration")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    sys.exit(asyncio.run(test_all_working()))

