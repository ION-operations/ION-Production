#!/usr/bin/env python3
"""
Test Multiple API Keys - Find Working Keys

Tests all provided API keys to identify which ones work.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent))

# Gemini API keys
GEMINI_KEYS = [
    "AIzaSyA9S1wxLNlvpx5g8A9UVS_TIJJVzngV_xY",
    "AIzaSyBbWCBLA4z0oNshsoXUcA55SaVulmBjQnU",
    "AIzaSyCLMMFKSF8RHrv2bfmJW_6yxeLygWD-3js",
    "AIzaSyCL2QTE7zT8oT6hC_GxM0Nt1p8QDmB5j7w",
    "AIzaSyC7a4hk3ddkD4OlyUk0vHC3bg1jkYml8-A",
]

# Cerebras API keys
CEREBRAS_KEYS = [
    "csk-prtm28t8d2wttrh5nwj63wpvy9xpejvymw84cm25dtrwhpht",
    "csk-xv6x26revypveycj6vffvf3yc4fhvx3mxwt9dy6de4xct5ty",
    "csk-p32pv3mykm96jrkj5cn38mf8nxhr988n5vdwrf6d5ep9kcyd",
    "csk-5vch3rmdnfyx8v3vmjw84r2e28wveychjyy48pdf4rmk3xdm",
]


async def test_gemini_key(key: str, index: int) -> tuple[bool, str]:
    """Test a single Gemini API key"""
    try:
        import google.generativeai as genai
        
        # Configure with this key
        genai.configure(api_key=key)
        
        # Try a simple API call
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Say 'Hello' in one word.")
        
        if response and hasattr(response, 'text'):
            return True, f"Success: {response.text[:50]}"
        else:
            return False, "No response text"
            
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return False, "Quota exceeded"
        elif "401" in error_msg or "403" in error_msg or "invalid" in error_msg.lower():
            return False, "Invalid key"
        else:
            return False, f"Error: {error_msg[:100]}"


async def test_cerebras_key(key: str, index: int) -> tuple[bool, str]:
    """Test a single Cerebras API key"""
    try:
        import httpx
        
        # Try different possible endpoints
        endpoints = [
            "https://api.cerebras.ai/v1/chat/completions",
            "https://api.cerebras.cloud/v1/chat/completions",
            "https://inference.cerebras.ai/v1/chat/completions",
        ]
        
        for endpoint in endpoints:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        endpoint,
                        headers={
                            "Authorization": f"Bearer {key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama-3.1-8b-instruct",
                            "messages": [{"role": "user", "content": "Say 'Hello' in one word."}],
                            "max_tokens": 10
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                        return True, f"Success (endpoint: {endpoint}): {content[:50]}"
                    elif response.status_code == 404:
                        # Try next endpoint
                        continue
                    elif response.status_code == 401 or response.status_code == 403:
                        return False, "Invalid key"
                    elif response.status_code == 429:
                        return False, "Rate limited"
                    else:
                        # Try next endpoint
                        continue
            except httpx.TimeoutException:
                continue
            except Exception as e:
                continue
        
        return False, "All endpoints failed (404 or error)"
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "403" in error_msg or "invalid" in error_msg.lower():
            return False, "Invalid key"
        else:
            return False, f"Error: {error_msg[:100]}"


async def main():
    """Test all API keys"""
    print("=" * 80)
    print("API KEY TESTING")
    print("=" * 80)
    
    print("\n" + "=" * 80)
    print("GEMINI API KEYS")
    print("=" * 80)
    
    gemini_results = []
    for i, key in enumerate(GEMINI_KEYS, 1):
        print(f"\n[TEST {i}/{len(GEMINI_KEYS)}] Testing Gemini key {i}...")
        print(f"   Key (first 20 chars): {key[:20]}...")
        
        success, message = await test_gemini_key(key, i)
        status = "[OK]" if success else "[FAIL]"
        print(f"   {status} {message}")
        
        gemini_results.append((i, key, success, message))
    
    print("\n" + "=" * 80)
    print("CEREBRAS API KEYS")
    print("=" * 80)
    
    cerebras_results = []
    for i, key in enumerate(CEREBRAS_KEYS, 1):
        print(f"\n[TEST {i}/{len(CEREBRAS_KEYS)}] Testing Cerebras key {i}...")
        print(f"   Key (first 20 chars): {key[:20]}...")
        
        success, message = await test_cerebras_key(key, i)
        status = "[OK]" if success else "[FAIL]"
        print(f"   {status} {message}")
        
        cerebras_results.append((i, key, success, message))
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    working_gemini = [r for r in gemini_results if r[2]]
    working_cerebras = [r for r in cerebras_results if r[2]]
    
    print(f"\nGemini: {len(working_gemini)}/{len(GEMINI_KEYS)} keys working")
    if working_gemini:
        print("   Working keys:")
        for idx, key, _, msg in working_gemini:
            print(f"      Key {idx}: {key[:30]}... ({msg[:50]})")
    
    print(f"\nCerebras: {len(working_cerebras)}/{len(CEREBRAS_KEYS)} keys working")
    if working_cerebras:
        print("   Working keys:")
        for idx, key, _, msg in working_cerebras:
            print(f"      Key {idx}: {key[:30]}... ({msg[:50]})")
    
    if not working_gemini and not working_cerebras:
        print("\n   [WARNING] No working keys found!")
    elif working_gemini or working_cerebras:
        print("\n   [SUCCESS] Found working keys!")
    
    return 0 if (working_gemini or working_cerebras) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

