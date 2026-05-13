#!/usr/bin/env python3
"""
Echo test for WebSocket connection
"""

import asyncio
import websockets

async def echo_test():
    """Test basic WebSocket connection."""
    
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected successfully")
            
            # Send a simple message
            await websocket.send("Hello, daemon!")
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"Received: {response}")
            
    except asyncio.TimeoutError:
        print("Timeout waiting for response")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(echo_test())
