#!/usr/bin/env python3
"""
HTTP-based Lucid Orchestrator Daemon
Simpler integration for IDE
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for IDE integration

TELEMETRY_PROGRESS_PATH = Path("ide_orchestration/telemetry/predictive_metrics.json")
CONFIDENCE_SNAPSHOT_PATH = Path("ide_orchestration/telemetry/confidence_routing_snapshot.json")

DEFAULT_PROGRESS_SNAPSHOT: Dict[str, Any] = {
    "description": "Prototype progress snapshot",
    "last_updated": "2025-11-07T00:00:00Z",
    "phases": {
        "research_phase": {
            "percent_complete": 40.0,
            "remaining_tasks": 3,
            "eta_days": 3.0,
            "velocity_tasks_per_day": 1.0,
        },
        "architecture_phase": {
            "percent_complete": 0.0,
            "remaining_tasks": 5,
            "eta_days": 5.0,
            "velocity_tasks_per_day": 1.0,
        },
    },
    "notes": "Fallback snapshot baked into daemon",
}

DEFAULT_CONFIDENCE_SNAPSHOT: Dict[str, Any] = {
    "tiers": [
        {
            "label": "Mastery",
            "range": "0.90 – 1.00",
            "description": "I've done this many times successfully",
            "strategy": "Execute immediately, high velocity",
            "validation": "Minimal – trust proven capability",
            "risk": "Very low",
            "examples": [
                "Organizational documentation",
                "Markdown/YAML structuring",
                "Reading existing code",
                "Git read-only operations",
            ],
        },
        {
            "label": "High Confidence",
            "range": "0.80 – 0.89",
            "description": "I've done similar work successfully",
            "strategy": "Execute with standard validation",
            "validation": "Normal testing, code review",
            "risk": "Low",
            "examples": [
                "HHNI optimization",
                "CMC queries",
                "Documentation expansion",
                "Test case writing",
            ],
        },
        {
            "label": "Medium Confidence",
            "range": "0.70 – 0.79",
            "description": "I understand theory, not much practice",
            "strategy": "Execute with extra validation",
            "validation": "Extensive testing, incremental progress",
            "risk": "Medium",
            "examples": ["VIF schema changes", "APOE parser", "SDF-CVF parity"],
        },
    ],
    "gitLevels": [
        {
            "level": "Low",
            "confidence_threshold": "0.60 – 0.75",
            "examples": ["git status/log/diff", "git add/commit", "git branch -c"],
            "strategy": "Execute with standard verification",
            "validation": "Inspect git state before operation",
            "risk": "Low – reversible",
        },
        {
            "level": "High",
            "confidence_threshold": "≥ 0.85",
            "examples": ["git push", "git reset --hard", "git rebase"],
            "strategy": "Mandatory verification before execution",
            "validation": "Confirm remote/branch, ensure clarity",
            "risk": "High – remote/destructive impact",
            "notes": "Push operations have high ambiguity risk",
        },
    ],
    "source": "knowledge_architecture/WORKFLOW_ORCHESTRATION/confidence_routing.md",
    "updated": "2025-10-22",
}

@dataclass
class SpecBlock:
    """SpecBlock model for doctrine layer."""
    node_id: str
    responsibility: str
    must_never: List[str]
    inputs: List[str]
    outputs: List[str]
    side_effects: List[str]
    security_level: str
    perf_budget_ms: int
    status: str
    drift_reason: Optional[str] = None
    governance: Optional[Dict[str, Any]] = None

@dataclass
class BlueprintNode:
    """Blueprint node model."""
    node_id: str
    name: str
    kind: str
    status: str
    security_level: Optional[str] = None

@dataclass
class BlueprintEdge:
    """Blueprint edge model."""
    node_id: str
    name: str
    kind: str
    status: str
    edge_type: str
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
    thread: str
    status: str
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
    """Lucid Orchestrator Daemon."""
    
    def __init__(self):
        self.focused_node = None
        self.mock_data = self._initialize_mock_data()
    
    def _initialize_mock_data(self) -> Dict[str, Any]:
        """Initialize comprehensive mock data."""
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
                "components:UserProfile": SpecBlock(
                    node_id="components:UserProfile",
                    responsibility="Display user profile information and handle profile updates",
                    must_never=[
                        "expose sensitive user data to unauthorized users",
                        "perform expensive operations on every render"
                    ],
                    inputs=["userId", "userData"],
                    outputs=["profileUI", "updateEvents"],
                    side_effects=["fetchUserData", "updateProfileCache"],
                    security_level="medium",
                    perf_budget_ms=100,
                    status="clean"
                ),
                "api:fetchUserData": SpecBlock(
                    node_id="api:fetchUserData",
                    responsibility="Fetch user data from the API with proper error handling",
                    must_never=[
                        "expose API keys in client-side code",
                        "make synchronous API calls",
                        "cache sensitive data without encryption"
                    ],
                    inputs=["userId", "authToken"],
                    outputs=["userData", "errorStatus"],
                    side_effects=["apiCall", "updateCache"],
                    security_level="high",
                    perf_budget_ms=500,
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
                ),
                "components:UserProfile": BlueprintSlice(
                    center=BlueprintNode(
                        node_id="components:UserProfile",
                        name="UserProfile",
                        kind="reactComponent",
                        status="clean",
                        security_level="medium"
                    ),
                    incoming=[
                        BlueprintEdge(
                            node_id="pages:ProfilePage",
                            name="ProfilePage",
                            kind="reactComponent",
                            status="clean",
                            edge_type="renders"
                        )
                    ],
                    outgoing=[
                        BlueprintEdge(
                            node_id="api:fetchUserData",
                            name="fetchUserData",
                            kind="function",
                            status="clean",
                            edge_type="calls"
                        ),
                        BlueprintEdge(
                            node_id="store:updateProfile",
                            name="updateProfile",
                            kind="function",
                            status="clean",
                            edge_type="calls"
                        )
                    ],
                    blast_radius={
                        "direct": 2,
                        "indirect": 4,
                        "risk_score": 0.3
                    }
                )
            },
            "progress_snapshot": DEFAULT_PROGRESS_SNAPSHOT,
            "confidence_snapshot": DEFAULT_CONFIDENCE_SNAPSHOT,
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
                        )
                    ]
                ),
                "components:UserProfile": TimelineSummary(
                    node_id="components:UserProfile",
                    recent_runs=[
                        TimelineRun(
                            timestamp=1730000001000,
                            duration_ms=25,
                            thread="main",
                            status="ok",
                            violations=[]
                        ),
                        TimelineRun(
                            timestamp=1730000002000,
                            duration_ms=18,
                            thread="main",
                            status="ok",
                            violations=[]
                        )
                    ],
                    worst_run_cascade=[
                        TimelineCascade(
                            symbol="UserProfile",
                            action="render",
                            duration_ms=0
                        ),
                        TimelineCascade(
                            symbol="fetchUserData",
                            action="call",
                            duration_ms=15
                        )
                    ]
                )
            }
        }
    
    def get_spec_block(self, node_id: str) -> Dict[str, Any]:
        """Get SpecBlock for a node."""
        if node_id not in self.mock_data["spec_blocks"]:
            # Return a default spec block for unknown nodes
            return asdict(SpecBlock(
                node_id=node_id,
                responsibility=f"Mock responsibility for {node_id}",
                must_never=["Mock constraint 1", "Mock constraint 2"],
                inputs=["input1", "input2"],
                outputs=["output1"],
                side_effects=["side_effect1"],
                security_level="medium",
                perf_budget_ms=100,
                status="clean"
            ))
        
        spec_block = self.mock_data["spec_blocks"][node_id]
        return asdict(spec_block)
    
    def get_blueprint_slice(self, node_id: str, depth: int = 1) -> Dict[str, Any]:
        """Get Blueprint slice for a node."""
        if node_id not in self.mock_data["blueprint_slices"]:
            # Return a default blueprint slice for unknown nodes
            return asdict(BlueprintSlice(
                center=BlueprintNode(
                    node_id=node_id,
                    name=node_id.split(':')[1] if ':' in node_id else 'unknown',
                    kind="function",
                    status="clean"
                ),
                incoming=[],
                outgoing=[],
                blast_radius={
                    "direct": 0,
                    "indirect": 0,
                    "risk_score": 0.0
                }
            ))
        
        blueprint_slice = self.mock_data["blueprint_slices"][node_id]
        return asdict(blueprint_slice)
    
    def get_timeline_summary(self, node_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get Timeline summary for a node."""
        if node_id not in self.mock_data["timeline_summaries"]:
            # Return a default timeline summary for unknown nodes
            return asdict(TimelineSummary(
                node_id=node_id,
                recent_runs=[],
                worst_run_cascade=[]
            ))
        
        timeline_summary = self.mock_data["timeline_summaries"][node_id]
        # Limit recent runs
        timeline_summary.recent_runs = timeline_summary.recent_runs[:limit]
        return asdict(timeline_summary)
    
    def propose_change(self, node_id: str) -> Dict[str, Any]:
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
                    "node_id": f"{node_id.split(':')[0]}:relatedNode",
                    "current_status": "clean",
                    "proposed_status": "drift",
                    "reason": "Performance impact from changes"
                }
            ],
            high_security_nodes=[f"{node_id.split(':')[0]}:securityNode"],
            risk_factors=[
                "Performance budget exceeded",
                "High security components affected",
                "UI thread blocking potential"
            ],
            required_mitigations=[
                "Update perf_budget_ms in SpecBlock",
                "Add performance monitoring",
                "Consider async loading"
            ],
            governance_template={
                "required_approvers": ["tech_lead", "security_reviewer"],
                "rationale_required": True,
                "risk_acceptance_required": True,
                "mitigation_plan_required": True
            }
        )
        
        return asdict(proposal)
    
    def focus_node(self, node_id: str) -> Dict[str, Any]:
        """Focus on a specific node."""
        self.focused_node = node_id
        logger.info(f"Focused on node: {node_id}")
        return {"success": True, "focused_node": node_id}

    def _load_snapshot_with_fallback(self, path: Path, fallback: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to load JSON snapshot from disk, fallback to provided default."""
        try:
            if path.exists():
                with path.open("r", encoding="utf-8") as fp:
                    return json.load(fp)
            logger.debug("Snapshot path %s not found, using fallback", path)
        except Exception as exc:
            logger.warning("Failed to read snapshot %s (%s)", path, exc)
        return fallback

    def get_progress_snapshot(self) -> Dict[str, Any]:
        """Return orchestrator progress telemetry."""
        return self._load_snapshot_with_fallback(
            TELEMETRY_PROGRESS_PATH, self.mock_data["progress_snapshot"]
        )

    def get_confidence_snapshot(self) -> Dict[str, Any]:
        """Return confidence routing snapshot."""
        return self._load_snapshot_with_fallback(
            CONFIDENCE_SNAPSHOT_PATH, self.mock_data["confidence_snapshot"]
        )

# Initialize daemon
daemon = LucidDaemon()

@app.route('/api/spec/<node_id>', methods=['GET'])
def get_spec_block(node_id):
    """Get SpecBlock for a node."""
    try:
        result = daemon.get_spec_block(node_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting spec block: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/blueprint/<node_id>', methods=['GET'])
def get_blueprint_slice(node_id):
    """Get Blueprint slice for a node."""
    try:
        depth = request.args.get('depth', 1, type=int)
        result = daemon.get_blueprint_slice(node_id, depth)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting blueprint slice: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/timeline/<node_id>', methods=['GET'])
def get_timeline_summary(node_id):
    """Get Timeline summary for a node."""
    try:
        limit = request.args.get('limit', 10, type=int)
        result = daemon.get_timeline_summary(node_id, limit)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting timeline summary: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/propose-change/<node_id>', methods=['POST'])
def propose_change(node_id):
    """Propose change for a node."""
    try:
        result = daemon.propose_change(node_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error proposing change: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/focus/<node_id>', methods=['POST'])
def focus_node(node_id):
    """Focus on a specific node."""
    try:
        result = daemon.focus_node(node_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error focusing node: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "focused_node": daemon.focused_node
    })

@app.route('/api/nodes', methods=['GET'])
def list_nodes():
    """List all available nodes."""
    nodes = []
    for node_id in daemon.mock_data["spec_blocks"].keys():
        nodes.append({
            "node_id": node_id,
            "name": node_id.split(':')[1] if ':' in node_id else node_id,
            "kind": daemon.mock_data["spec_blocks"][node_id].kind if hasattr(daemon.mock_data["spec_blocks"][node_id], 'kind') else 'function'
        })
    return jsonify(nodes)

@app.route('/api/telemetry/progress', methods=['GET'])
def get_progress_snapshot():
    """Expose orchestrator progress telemetry."""
    try:
        return jsonify(daemon.get_progress_snapshot())
    except Exception as e:
        logger.error(f"Error loading progress telemetry: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/telemetry/confidence-routing', methods=['GET'])
def get_confidence_snapshot():
    """Expose confidence routing snapshot."""
    try:
        return jsonify(daemon.get_confidence_snapshot())
    except Exception as e:
        logger.error(f"Error loading confidence telemetry: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Lucid Orchestrator HTTP Daemon on http://localhost:5000")
    logger.info("Available endpoints:")
    logger.info("  GET  /api/health")
    logger.info("  GET  /api/nodes")
    logger.info("  GET  /api/spec/<node_id>")
    logger.info("  GET  /api/blueprint/<node_id>?depth=1")
    logger.info("  GET  /api/timeline/<node_id>?limit=10")
    logger.info("  POST /api/propose-change/<node_id>")
    logger.info("  POST /api/focus/<node_id>")
    logger.info("  GET  /api/telemetry/progress")
    logger.info("  GET  /api/telemetry/confidence-routing")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
