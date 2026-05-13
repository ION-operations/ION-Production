#!/usr/bin/env python3
"""
Simple test for Lucid Orchestrator Daemon
"""

import asyncio
import json
import websockets

async def simple_test():
    """Simple test of the daemon."""
    
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to Lucid Daemon")
            
            # Simple test request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSpecBlock",
                "params": {"nodeId": "auth/session:rehydrateSession"}
            }
            
            print("Sending request:", json.dumps(request, indent=2))
            await websocket.send(json.dumps(request))
            
            response = await websocket.recv()
            print("Received response:", response)
            
            result = json.loads(response)
            print("Parsed result:", json.dumps(result, indent=2))
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(simple_test())
