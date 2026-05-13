#!/usr/bin/env python3
"""
Lucid Orchestrator Daemon
Provides the nervous system for the Lucid Orchestrator extension.
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SpecBlock:
    """SpecBlock model for doctrine layer."""
    node_id: str
    responsibility: str
    must_never: List[str]
    inputs: List[str]
    outputs: List[str]
    side_effects: List[str]
    security_level: str  # low, medium, high, critical
    perf_budget_ms: int
    status: str  # clean, drift, violation, proposed
    drift_reason: Optional[str] = None
    governance: Optional[Dict[str, Any]] = None

@dataclass
class BlueprintNode:
    """Blueprint node model."""
    node_id: str
    name: str
    kind: str  # function, reactComponent, store, job, etc.
    status: str  # clean, drift, violation
    security_level: Optional[str] = None

@dataclass
class BlueprintEdge:
    """Blueprint edge model."""
    node_id: str
    name: str
    kind: str
    status: str
    edge_type: str  # calls, updatesUI, queriesDB, publishesEvent, etc.
    security_level: Optional[str] = None

@dataclass
class BlueprintSlice:
    """Blueprint slice response."""
    center: BlueprintNode
    incoming: List[BlueprintEdge]
    outgoing: List[BlueprintEdge]
    blast_radius: Dict[str, Any]

@dataclass
class TimelineRun:
    """Timeline run model."""
    timestamp: int
    duration_ms: int
    thread: str  # main, worker, server
    status: str  # normal, slow, threw, security_event
    violations: List[str]

@dataclass
class TimelineCascade:
    """Timeline cascade model."""
    symbol: str
    action: str
    duration_ms: int
    thread: Optional[str] = None

@dataclass
class TimelineSummary:
    """Timeline summary response."""
    node_id: str
    recent_runs: List[TimelineRun]
    worst_run_cascade: List[TimelineCascade]

@dataclass
class ChangeProposal:
    """Change proposal response."""
    node_id: str
    blast_radius_summary: Dict[str, Any]
    affected_specs: List[Dict[str, Any]]
    high_security_nodes: List[str]
    risk_factors: List[str]
    required_mitigations: List[str]
    governance_template: Dict[str, Any]

class LucidDaemon:
    """Lucid Orchestrator Daemon - the nervous system."""
    
    def __init__(self):
        self.connections = set()
        self.focused_node = None
        self.mock_data = self._initialize_mock_data()
    
    def _initialize_mock_data(self) -> Dict[str, Any]:
        """Initialize mock data for development."""
        return {
            "spec_blocks": {
                "auth/session:rehydrateSession": SpecBlock(
                    node_id="auth/session:rehydrateSession",
                    responsibility="Rehydrate user session from stored credentials and validate authentication state",
                    must_never=[
                        "expose raw auth token to UI state",
                        "block main thread >20ms",
                        "store credentials in localStorage without encryption"
                    ],
                    inputs=["storedCredentials", "sessionConfig"],
                    outputs=["sessionState", "authStatus"],
                    side_effects=["updateAuthStore", "triggerReauthIfNeeded"],
                    security_level="high",
                    perf_budget_ms=20,
                    status="drift",
                    drift_reason="blocked main thread 42ms",
                    governance={
                        "lastChange": {
                            "by": "braden",
                            "at": "2025-10-27T03:12:11Z",
                            "reason": "accepted temporary perf regression for session restore"
                        }
                    }
                ),
                "auth/store:updateSession": SpecBlock(
                    node_id="auth/store:updateSession",
                    responsibility="Update session state in the authentication store",
                    must_never=[
                        "expose session data to non-authorized components",
                        "perform synchronous operations >5ms"
                    ],
                    inputs=["sessionData", "authToken"],
                    outputs=["updatedSessionState"],
                    side_effects=["notifySubscribers", "updateLocalStorage"],
                    security_level="critical",
                    perf_budget_ms=5,
                    status="clean"
                )
            },
            "blueprint_slices": {
                "auth/session:rehydrateSession": BlueprintSlice(
                    center=BlueprintNode(
                        node_id="auth/session:rehydrateSession",
                        name="rehydrateSession",
                        kind="function",
                        status="drift",
                        security_level="high"
                    ),
                    incoming=[
                        BlueprintEdge(
                            node_id="app/boot:AppBootSequence",
                            name="AppBootSequence",
                            kind="job",
                            status="clean",
                            edge_type="calls"
                        )
                    ],
                    outgoing=[
                        BlueprintEdge(
                            node_id="auth/components:SessionProvider",
                            name="SessionProvider",
                            kind="reactComponent",
                            status="violation",
                            security_level="critical",
                            edge_type="updatesUI"
                        ),
                        BlueprintEdge(
                            node_id="auth/store:updateSession",
                            name="authStore.updateSession",
                            kind="store",
                            status="clean",
                            edge_type="mutates"
                        )
                    ],
                    blast_radius={
                        "direct": 3,
                        "indirect": 7,
                        "risk_score": 0.82
                    }
                )
            },
            "timeline_summaries": {
                "auth/session:rehydrateSession": TimelineSummary(
                    node_id="auth/session:rehydrateSession",
                    recent_runs=[
                        TimelineRun(
                            timestamp=1730000000000,
                            duration_ms=42,
                            thread="main",
                            status="slow",
                            violations=["perf_budget_exceeded"]
                        ),
                        TimelineRun(
                            timestamp=1730000000123,
                            duration_ms=8,
                            thread="main",
                            status="ok",
                            violations=[]
                        )
                    ],
                    worst_run_cascade=[
                        TimelineCascade(
                            symbol="rehydrateSession",
                            action="start",
                            duration_ms=0
                        ),
                        TimelineCascade(
                            symbol="fetch(/auth/refresh)",
                            action="await",
                            duration_ms=31
                        ),
                        TimelineCascade(
                            symbol="authStore.updateSession",
                            action="commit",
                            duration_ms=3
                        ),
                        TimelineCascade(
                            symbol="SessionProvider",
                            action="re-render",
                            duration_ms=8,
                            thread="main"
                        )
                    ]
                )
            }
        }
    
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
            
            # Route to appropriate handler
            if method == "getSpecBlock":
                result = await self.get_spec_block(params.get("nodeId"))
            elif method == "getBlueprintSlice":
                result = await self.get_blueprint_slice(
                    params.get("nodeId"), 
                    params.get("depth", 1)
                )
            elif method == "getTimelineSummary":
                result = await self.get_timeline_summary(
                    params.get("nodeId"),
                    params.get("limit", 10)
                )
            elif method == "proposeChange":
                result = await self.propose_change(params.get("nodeId"))
            elif method == "focusNode":
                result = await self.focus_node(params.get("nodeId"))
            else:
                result = {"error": f"Unknown method: {method}"}
            
            # Send response
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
            await websocket.send(json.dumps(response, default=str))
            
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
    
    async def get_spec_block(self, node_id: str) -> Dict[str, Any]:
        """Get SpecBlock for a node."""
        if node_id not in self.mock_data["spec_blocks"]:
            return {"error": f"SpecBlock not found for node: {node_id}"}
        
        spec_block = self.mock_data["spec_blocks"][node_id]
        return asdict(spec_block)
    
    async def get_blueprint_slice(self, node_id: str, depth: int = 1) -> Dict[str, Any]:
        """Get Blueprint slice for a node."""
        if node_id not in self.mock_data["blueprint_slices"]:
            return {"error": f"Blueprint slice not found for node: {node_id}"}
        
        blueprint_slice = self.mock_data["blueprint_slices"][node_id]
        return asdict(blueprint_slice)
    
    async def get_timeline_summary(self, node_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get Timeline summary for a node."""
        if node_id not in self.mock_data["timeline_summaries"]:
            return {"error": f"Timeline summary not found for node: {node_id}"}
        
        timeline_summary = self.mock_data["timeline_summaries"][node_id]
        # Limit recent runs
        timeline_summary.recent_runs = timeline_summary.recent_runs[:limit]
        return asdict(timeline_summary)
    
    async def propose_change(self, node_id: str) -> Dict[str, Any]:
        """Propose change for a node."""
        # Mock change proposal
        proposal = ChangeProposal(
            node_id=node_id,
            blast_radius_summary={
                "direct_affected": 3,
                "indirect_affected": 7,
                "risk_score": 0.82,
                "high_risk_areas": ["auth", "session", "ui"]
            },
            affected_specs=[
                {
                    "node_id": "auth/components:SessionProvider",
                    "current_status": "clean",
                    "proposed_status": "drift",
                    "reason": "Performance impact from session rehydration"
                }
            ],
            high_security_nodes=["auth/store:updateSession", "auth/components:SessionProvider"],
            risk_factors=[
                "Performance budget exceeded",
                "High security components affected",
                "UI thread blocking potential"
            ],
            required_mitigations=[
                "Update perf_budget_ms in SpecBlock",
                "Add performance monitoring",
                "Consider async session loading"
            ],
            governance_template={
                "required_approvers": ["tech_lead", "security_reviewer"],
                "rationale_required": True,
                "risk_acceptance_required": True,
                "mitigation_plan_required": True
            }
        )
        
        return asdict(proposal)
    
    async def focus_node(self, node_id: str) -> Dict[str, Any]:
        """Focus on a specific node."""
        self.focused_node = node_id
        logger.info(f"Focused on node: {node_id}")
        
        # Broadcast focus change to all connected clients
        focus_message = {
            "type": "node_focused",
            "node_id": node_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_all(focus_message)
        
        return {"success": True, "focused_node": node_id}
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        if not self.connections:
            return
        
        message_str = json.dumps(message, default=str)
        disconnected = set()
        
        for websocket in self.connections:
            try:
                await websocket.send(message_str)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(websocket)
        
        # Remove disconnected clients
        self.connections -= disconnected

async def main():
    """Main daemon entry point."""
    daemon = LucidDaemon()
    
    logger.info("Starting Lucid Orchestrator Daemon on ws://localhost:8765")
    
    async with websockets.serve(daemon.handle_connection, "localhost", 8765):
        logger.info("Daemon running. Press Ctrl+C to stop.")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Daemon stopped")
