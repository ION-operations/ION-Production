#!/usr/bin/env python3
"""
Test New Gemini Key

Tests the new Gemini API key.
"""

import os
import sys
import asyncio
from pathlib import Path

# New Gemini key
NEW_GEMINI_KEY = "AIzaSyDiZIEkjqgyJSmQsBYnYuo69fAlkEsgplI"

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_new_gemini_key():
    """Test the new Gemini key"""
    print("=" * 80)
    print("TEST: New Gemini Key")
    print("=" * 80)
    
    try:
        import google.generativeai as genai
        
        # Configure with new key
        genai.configure(api_key=NEW_GEMINI_KEY)
        
        # Try a simple API call
        print(f"\n[TEST] Testing key: {NEW_GEMINI_KEY[:30]}...")
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Say 'Hello, AIM-OS!' in one sentence.")
        
        if response and hasattr(response, 'text'):
            print(f"\n[RESULT] Success!")
            print(f"   Response: {response.text.strip()}")
            print(f"   Key: {NEW_GEMINI_KEY}")
            return True, "Success"
        else:
            print(f"\n[RESULT] No response text")
            return False, "No response text"
            
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower() or "RESOURCE_EXHAUSTED" in error_msg:
            print(f"\n[RESULT] Quota exceeded")
            return False, "Quota exceeded"
        elif "401" in error_msg or "403" in error_msg or "invalid" in error_msg.lower() or "INVALID_ARGUMENT" in error_msg:
            print(f"\n[RESULT] Invalid key")
            return False, "Invalid key"
        elif "PERMISSION_DENIED" in error_msg:
            print(f"\n[RESULT] Permission denied")
            return False, "Permission denied"
        else:
            print(f"\n[RESULT] Error: {error_msg[:100]}")
            return False, f"Error: {error_msg[:100]}"


async def main():
    """Run test"""
    success, message = await test_new_gemini_key()
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if success:
        print(f"   [SUCCESS] New Gemini key is working!")
        print(f"\n   Working Key:")
        print(f"   {NEW_GEMINI_KEY}")
        print(f"\n   Status: Ready for use")
        return 0
    else:
        print(f"   [FAIL] New Gemini key failed: {message}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

