#!/usr/bin/env python3
"""
Comprehensive API Key Testing

Tests all provided API keys with correct endpoints.
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
            return True, f"Success: {response.text.strip()}"
        else:
            return False, "No response text"
            
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower() or "RESOURCE_EXHAUSTED" in error_msg:
            return False, "Quota exceeded"
        elif "401" in error_msg or "403" in error_msg or "invalid" in error_msg.lower() or "INVALID_ARGUMENT" in error_msg:
            return False, "Invalid key"
        elif "PERMISSION_DENIED" in error_msg:
            return False, "Permission denied"
        else:
            return False, f"Error: {error_msg[:80]}"


async def test_cerebras_key_models(key: str, index: int) -> tuple[bool, str]:
    """Test Cerebras key with /models endpoint"""
    try:
        import httpx
        
        # Try /models endpoint first
        endpoint = "https://api.cerebras.ai/v1/models"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                endpoint,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                models = result.get("data", [])
                model_names = [m.get("id", "unknown") for m in models[:3]]
                return True, f"Success - Found {len(models)} models: {', '.join(model_names)}"
            elif response.status_code == 401 or response.status_code == 403:
                return False, "Invalid key"
            elif response.status_code == 404:
                return False, "Endpoint not found"
            elif response.status_code == 429:
                return False, "Rate limited"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:80]}"
                
    except httpx.TimeoutException:
        return False, "Timeout"
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "403" in error_msg or "invalid" in error_msg.lower():
            return False, "Invalid key"
        else:
            return False, f"Error: {error_msg[:80]}"


async def test_cerebras_key_chat(key: str, index: int) -> tuple[bool, str]:
    """Test Cerebras key with /chat/completions endpoint"""
    try:
        import httpx
        
        # Try /chat/completions endpoint
        endpoint = "https://api.cerebras.ai/v1/chat/completions"
        
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
                return True, f"Success: {content.strip()}"
            elif response.status_code == 401 or response.status_code == 403:
                return False, "Invalid key"
            elif response.status_code == 404:
                return False, "Endpoint not found"
            elif response.status_code == 429:
                return False, "Rate limited"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:80]}"
                
    except httpx.TimeoutException:
        return False, "Timeout"
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "403" in error_msg or "invalid" in error_msg.lower():
            return False, "Invalid key"
        else:
            return False, f"Error: {error_msg[:80]}"


async def main():
    """Test all API keys"""
    print("=" * 80)
    print("COMPREHENSIVE API KEY TESTING")
    print("=" * 80)
    
    print("\n" + "=" * 80)
    print("GEMINI API KEYS (Re-testing All)")
    print("=" * 80)
    
    gemini_results = []
    for i, key in enumerate(GEMINI_KEYS, 1):
        print(f"\n[TEST {i}/{len(GEMINI_KEYS)}] Testing Gemini key {i}...")
        print(f"   Key (first 30 chars): {key[:30]}...")
        
        success, message = await test_gemini_key(key, i)
        status = "[OK]" if success else "[FAIL]"
        print(f"   {status} {message}")
        
        gemini_results.append((i, key, success, message))
    
    print("\n" + "=" * 80)
    print("CEREBRAS API KEYS - /models Endpoint")
    print("=" * 80)
    
    cerebras_models_results = []
    for i, key in enumerate(CEREBRAS_KEYS, 1):
        print(f"\n[TEST {i}/{len(CEREBRAS_KEYS)}] Testing Cerebras key {i} (/models)...")
        print(f"   Key (first 30 chars): {key[:30]}...")
        
        success, message = await test_cerebras_key_models(key, i)
        status = "[OK]" if success else "[FAIL]"
        print(f"   {status} {message}")
        
        cerebras_models_results.append((i, key, success, message))
    
    print("\n" + "=" * 80)
    print("CEREBRAS API KEYS - /chat/completions Endpoint")
    print("=" * 80)
    
    cerebras_chat_results = []
    for i, key in enumerate(CEREBRAS_KEYS, 1):
        print(f"\n[TEST {i}/{len(CEREBRAS_KEYS)}] Testing Cerebras key {i} (/chat/completions)...")
        print(f"   Key (first 30 chars): {key[:30]}...")
        
        success, message = await test_cerebras_key_chat(key, i)
        status = "[OK]" if success else "[FAIL]"
        print(f"   {status} {message}")
        
        cerebras_chat_results.append((i, key, success, message))
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    working_gemini = [r for r in gemini_results if r[2]]
    working_cerebras_models = [r for r in cerebras_models_results if r[2]]
    working_cerebras_chat = [r for r in cerebras_chat_results if r[2]]
    
    print(f"\nGemini: {len(working_gemini)}/{len(GEMINI_KEYS)} keys working")
    if working_gemini:
        print("   Working keys:")
        for idx, key, _, msg in working_gemini:
            print(f"      Key {idx}: {key[:40]}... ({msg[:60]})")
    else:
        print("   No working keys found")
        print("   Issues:")
        for idx, key, _, msg in gemini_results:
            print(f"      Key {idx}: {msg}")
    
    print(f"\nCerebras (/models): {len(working_cerebras_models)}/{len(CEREBRAS_KEYS)} keys working")
    if working_cerebras_models:
        print("   Working keys:")
        for idx, key, _, msg in working_cerebras_models:
            print(f"      Key {idx}: {key[:40]}... ({msg[:60]})")
    else:
        print("   No working keys found")
        print("   Issues:")
        for idx, key, _, msg in cerebras_models_results:
            print(f"      Key {idx}: {msg}")
    
    print(f"\nCerebras (/chat/completions): {len(working_cerebras_chat)}/{len(CEREBRAS_KEYS)} keys working")
    if working_cerebras_chat:
        print("   Working keys:")
        for idx, key, _, msg in working_cerebras_chat:
            print(f"      Key {idx}: {key[:40]}... ({msg[:60]})")
    else:
        print("   No working keys found")
        print("   Issues:")
        for idx, key, _, msg in cerebras_chat_results:
            print(f"      Key {idx}: {msg}")
    
    total_working = len(working_gemini) + len(working_cerebras_models) + len(working_cerebras_chat)
    if total_working > 0:
        print(f"\n   [SUCCESS] Found {total_working} working key/endpoint combination(s)!")
    else:
        print("\n   [WARNING] No working keys found!")
    
    return 0 if total_working > 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

