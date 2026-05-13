#!/usr/bin/env python3
"""
Test Cerebras API Endpoints

Tests various Cerebras API endpoints to find the correct chat endpoint.
"""

import asyncio
import httpx

CEREBRAS_KEY = "csk-prtm28t8d2wttrh5nwj63wpvy9xpejvymw84cm25dtrwhpht"
BASE_URL = "https://api.cerebras.ai/v1"

async def test_endpoint(endpoint: str, method: str = "GET", data: dict = None):
    """Test a specific endpoint"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if method == "GET":
                response = await client.get(
                    f"{BASE_URL}{endpoint}",
                    headers={
                        "Authorization": f"Bearer {CEREBRAS_KEY}",
                        "Content-Type": "application/json"
                    }
                )
            else:
                response = await client.post(
                    f"{BASE_URL}{endpoint}",
                    headers={
                        "Authorization": f"Bearer {CEREBRAS_KEY}",
                        "Content-Type": "application/json"
                    },
                    json=data or {}
                )
            
            print(f"\n{method} {endpoint}:")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"   Response: {str(result)[:200]}...")
                    return True, result
                except:
                    print(f"   Response: {response.text[:200]}")
                    return True, response.text
            else:
                print(f"   Error: {response.text[:200]}")
                return False, response.text
    except Exception as e:
        print(f"   Exception: {str(e)[:200]}")
        return False, str(e)

async def main():
    """Test various endpoints"""
    print("=" * 80)
    print("CEREBRAS API ENDPOINT DISCOVERY")
    print("=" * 80)
    
    # Test known working endpoint
    print("\n[TEST] Known working endpoint:")
    await test_endpoint("/models", "GET")
    
    # Test various chat/completions endpoints
    print("\n[TEST] Testing chat/completions endpoints:")
    endpoints_to_test = [
        ("/chat/completions", "POST", {
            "model": "llama3.1-8b",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }),
        ("/completions", "POST", {
            "model": "llama3.1-8b",
            "prompt": "Hello",
            "max_tokens": 10
        }),
        ("/v1/completions", "POST", {
            "model": "llama3.1-8b",
            "prompt": "Hello",
            "max_tokens": 10
        }),
        ("/generate", "POST", {
            "model": "llama3.1-8b",
            "prompt": "Hello",
            "max_tokens": 10
        }),
    ]
    
    for endpoint, method, data in endpoints_to_test:
        success, result = await test_endpoint(endpoint, method, data)
        if success:
            print(f"\n   [SUCCESS] Found working endpoint: {endpoint}")
            break
    
    # Check models to see what's available
    print("\n[TEST] Available models:")
    success, models_result = await test_endpoint("/models", "GET")
    if success and isinstance(models_result, dict):
        models = models_result.get("data", [])
        print(f"\n   Found {len(models)} models:")
        for model in models[:10]:
            model_id = model.get("id", "unknown")
            print(f"      - {model_id}")

if __name__ == "__main__":
    asyncio.run(main())

