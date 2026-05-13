#!/usr/bin/env python3
"""
Minimal Lucid Orchestrator Daemon for testing
"""

import asyncio
import json
import websockets
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinimalDaemon:
    """Minimal daemon implementation."""
    
    def __init__(self):
        self.connections = set()
    
    async def handle_connection(self, websocket, path):
        """Handle WebSocket connection."""
        self.connections.add(websocket)
        logger.info(f"Client connected. Total connections: {len(self.connections)}")
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        finally:
            self.connections.discard(websocket)
    
    async def handle_message(self, websocket, message):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            method = data.get("method")
            params = data.get("params", {})
            request_id = data.get("id")
            
            logger.info(f"Received request: {method}")
            
            # Simple mock responses
            if method == "getSpecBlock":
                result = {
                    "node_id": params.get("nodeId", "unknown"),
                    "responsibility": "Mock responsibility",
                    "must_never": ["Mock constraint 1", "Mock constraint 2"],
                    "inputs": ["input1", "input2"],
                    "outputs": ["output1"],
                    "side_effects": ["side_effect1"],
                    "security_level": "high",
                    "perf_budget_ms": 100,
                    "status": "clean"
                }
            elif method == "getBlueprintSlice":
                result = {
                    "center": {
                        "node_id": params.get("nodeId", "unknown"),
                        "name": "mockFunction",
                        "kind": "function",
                        "status": "clean"
                    },
                    "incoming": [],
                    "outgoing": [],
                    "blast_radius": {
                        "direct": 0,
                        "indirect": 0,
                        "risk_score": 0.0
                    }
                }
            elif method == "getTimelineSummary":
                result = {
                    "node_id": params.get("nodeId", "unknown"),
                    "recent_runs": [],
                    "worst_run_cascade": []
                }
            elif method == "proposeChange":
                result = {
                    "node_id": params.get("nodeId", "unknown"),
                    "blast_radius_summary": {"risk_score": 0.5},
                    "affected_specs": [],
                    "high_security_nodes": [],
                    "risk_factors": [],
                    "required_mitigations": [],
                    "governance_template": {}
                }
            elif method == "focusNode":
                result = {"success": True, "focused_node": params.get("nodeId", "unknown")}
            else:
                result = {"error": f"Unknown method: {method}"}
            
            # Send response
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
            await websocket.send(json.dumps(response))
            logger.info(f"Sent response for {method}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            await websocket.send(json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            }))
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await websocket.send(json.dumps({
                "jsonrpc": "2.0",
                "id": data.get("id") if 'data' in locals() else None,
                "error": {"code": -32603, "message": "Internal error"}
            }))

async def main():
    """Main daemon entry point."""
    daemon = MinimalDaemon()
    
    logger.info("Starting Minimal Lucid Daemon on ws://localhost:8765")
    
    async with websockets.serve(daemon.handle_connection, "localhost", 8765):
        logger.info("Daemon running. Press Ctrl+C to stop.")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Daemon stopped")
