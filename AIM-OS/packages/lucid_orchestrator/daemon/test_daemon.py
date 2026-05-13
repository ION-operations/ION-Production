#!/usr/bin/env python3
"""
Test script for Lucid Orchestrator Daemon
"""

import asyncio
import json
import websockets
import sys

async def test_daemon():
    """Test the daemon WebSocket API."""
    
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("+ Connected to Lucid Daemon")
            
            # Test getSpecBlock
            print("\nTesting getSpecBlock...")
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSpecBlock",
                "params": {"nodeId": "auth/session:rehydrateSession"}
            }
            
            await websocket.send(json.dumps(request))
            response = await websocket.recv()
            result = json.loads(response)
            
            if "result" in result:
                print("+ getSpecBlock successful")
                print(f"  Node ID: {result['result']['node_id']}")
                print(f"  Status: {result['result']['status']}")
                print(f"  Responsibility: {result['result']['responsibility'][:50]}...")
            else:
                print(f"- getSpecBlock failed: {result.get('error', 'Unknown error')}")
            
            # Test getBlueprintSlice
            print("\nTesting getBlueprintSlice...")
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "getBlueprintSlice",
                "params": {"nodeId": "auth/session:rehydrateSession", "depth": 1}
            }
            
            await websocket.send(json.dumps(request))
            response = await websocket.recv()
            result = json.loads(response)
            
            if "result" in result:
                print("+ getBlueprintSlice successful")
                print(f"  Center: {result['result']['center']['name']}")
                print(f"  Incoming: {len(result['result']['incoming'])} nodes")
                print(f"  Outgoing: {len(result['result']['outgoing'])} nodes")
                print(f"  Blast Radius: {result['result']['blast_radius']['direct']} direct, {result['result']['blast_radius']['indirect']} indirect")
            else:
                print(f"- getBlueprintSlice failed: {result.get('error', 'Unknown error')}")
            
            # Test getTimelineSummary
            print("\nTesting getTimelineSummary...")
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "getTimelineSummary",
                "params": {"nodeId": "auth/session:rehydrateSession", "limit": 5}
            }
            
            await websocket.send(json.dumps(request))
            response = await websocket.recv()
            result = json.loads(response)
            
            if "result" in result:
                print("+ getTimelineSummary successful")
                print(f"  Recent Runs: {len(result['result']['recent_runs'])}")
                print(f"  Worst Cascade: {len(result['result']['worst_run_cascade'])} steps")
            else:
                print(f"- getTimelineSummary failed: {result.get('error', 'Unknown error')}")
            
            # Test proposeChange
            print("\nTesting proposeChange...")
            request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "proposeChange",
                "params": {"nodeId": "auth/session:rehydrateSession"}
            }
            
            await websocket.send(json.dumps(request))
            response = await websocket.recv()
            result = json.loads(response)
            
            if "result" in result:
                print("+ proposeChange successful")
                print(f"  Risk Score: {result['result']['blast_radius_summary']['risk_score']}")
                print(f"  High Security Nodes: {len(result['result']['high_security_nodes'])}")
                print(f"  Risk Factors: {len(result['result']['risk_factors'])}")
            else:
                print(f"- proposeChange failed: {result.get('error', 'Unknown error')}")
            
            # Test focusNode
            print("\nTesting focusNode...")
            request = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "focusNode",
                "params": {"nodeId": "auth/session:rehydrateSession"}
            }
            
            await websocket.send(json.dumps(request))
            response = await websocket.recv()
            result = json.loads(response)
            
            if "result" in result:
                print("+ focusNode successful")
                print(f"  Focused Node: {result['result']['focused_node']}")
            else:
                print(f"- focusNode failed: {result.get('error', 'Unknown error')}")
            
            print("\n+ All tests completed successfully!")
            
    except ConnectionRefusedError:
        print("- Connection refused. Is the daemon running?")
        print("  Start it with: python packages/lucid_orchestrator/daemon/run_daemon.py")
        sys.exit(1)
    except Exception as e:
        print(f"- Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_daemon())
