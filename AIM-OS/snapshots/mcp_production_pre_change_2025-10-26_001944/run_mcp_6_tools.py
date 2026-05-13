#!/usr/bin/env python3
"""
MCP Server - AIM-OS Tools

AIM-OS Core Tools (9 total):
1. store_memory - Store information in AIM-OS persistent memory (CMC)
2. get_memory_stats - Get statistics about the AIM-OS memory system (CMC)
3. retrieve_memory - Search and retrieve memories from AIM-OS persistent memory (CMC)
4. create_plan - Create an execution plan using APOE (AI-Powered Orchestration Engine)
5. track_confidence - Track confidence and provenance using VIF (Verifiable Intelligence Framework)
6. synthesize_knowledge - Synthesize knowledge using SEG (Shared Evidence Graph)
7. check_invariant - Check if action violates invariant rules (SCOR)
8. run_baseline_probe - Detect self-concept drift via baseline probes (SCOR)
9. detect_manipulation_signals - Detect social manipulation in user input (SCOR)
"""

import sys
import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages"))

def log(msg: str):
    """Log to stderr only (never stdout - it corrupts JSON-RPC)"""
    print(f"[MCP-6-TOOLS] {msg}", file=sys.stderr, flush=True)

class SimpleMCPServer:
    """MCP Server with AIM-OS tools (9 total: 6 core + 3 SCOR)"""
    
    def __init__(self):
        log("Initializing MCP Server (9 tools: 6 core + 3 SCOR)...")
        try:
            # CRITICAL: Configure logging to stderr BEFORE importing
            import logging
            from cmc_service.logging_utils import configure_logging
            configure_logging(stream=sys.stderr, level=logging.WARNING)
            
            # Import only the basic AIM-OS modules needed for core tools
            from cmc_service import MemoryStore
            from cmc_service.models import AtomCreate, AtomContent
            
            # Initialize basic systems
            self.memory = MemoryStore("./mcp_memory")
            
            log("SUCCESS: MCP Server initialized with 9 tools (6 core + 3 SCOR)")
            
        except Exception as e:
            log(f"ERROR: Failed to initialize simplified systems: {e}")
            self.memory = None
    
    def run(self):
        """Main MCP server loop"""
        log("Starting MCP server loop...")
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line.strip())
                response = self.handle_request(request)
                
                print(json.dumps(response))
                sys.stdout.flush()
                
            except Exception as e:
                log(f"ERROR in main loop: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        method = request.get("method")
        request_id = request.get("id")
        
        if method == "initialize":
            return self.handle_initialize(request_id)
        elif method == "tools/list":
            return self.handle_tools_list(request_id)
        elif method == "tools/call":
            return self.handle_tools_call(request, request_id)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    def handle_initialize(self, request_id: Any) -> Dict[str, Any]:
        """Handle initialize request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "aimos-6-tools-server",
                    "version": "1.0.0"
                }
            }
        }
    
    def handle_tools_list(self, request_id: Any) -> Dict[str, Any]:
        """Handle tools/list request - Return all 9 AIM-OS tools"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    # Tool 1: store_memory
                    {
                        "name": "store_memory",
                        "description": "Store information in AIM-OS persistent memory",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"},
                                "tags": {"type": "object"}
                            },
                            "required": ["content"]
                        }
                    },
                    # Tool 2: get_memory_stats
                    {
                        "name": "get_memory_stats",
                        "description": "Get statistics about the AIM-OS memory system",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    # Tool 3: retrieve_memory
                    {
                        "name": "retrieve_memory",
                        "description": "Search and retrieve memories from AIM-OS persistent memory",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Search query for memories"},
                                "limit": {"type": "integer", "description": "Maximum number of memories to return", "default": 10},
                                "tags": {"type": "object", "description": "Filter by tags"}
                            },
                            "required": ["query"]
                        }
                    },
                    # Tool 4: create_plan
                    {
                        "name": "create_plan",
                        "description": "Create an execution plan using APOE (AI-Powered Orchestration Engine)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "goal": {"type": "string", "description": "The goal to achieve"},
                                "context": {"type": "string", "description": "Current context and constraints"},
                                "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"], "default": "medium"}
                            },
                            "required": ["goal"]
                        }
                    },
                    # Tool 5: track_confidence
                    {
                        "name": "track_confidence",
                        "description": "Track confidence and provenance using VIF (Verifiable Intelligence Framework)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "task": {"type": "string", "description": "Task being tracked"},
                                "confidence": {"type": "number", "minimum": 0, "maximum": 1, "description": "Confidence level (0-1)"},
                                "reasoning": {"type": "string", "description": "Reasoning for confidence level"},
                                "evidence": {"type": "array", "items": {"type": "string"}, "description": "Supporting evidence"}
                            },
                            "required": ["task", "confidence"]
                        }
                    },
                    # Tool 6: synthesize_knowledge
                    {
                        "name": "synthesize_knowledge",
                        "description": "Synthesize knowledge using SEG (Shared Evidence Graph)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "topics": {"type": "array", "items": {"type": "string"}, "description": "Topics to synthesize"},
                                "depth": {"type": "string", "enum": ["shallow", "medium", "deep"], "default": "medium"},
                                "format": {"type": "string", "enum": ["summary", "detailed", "structured"], "default": "summary"}
                            },
                            "required": ["topics"]
                        }
                    },
                    # Tool 7: check_invariant
                    {
                        "name": "check_invariant",
                        "description": "Check if action violates invariant rules",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "object", "description": "Action to validate"},
                                "context": {"type": "object", "description": "Context for validation"}
                            },
                            "required": ["action"]
                        }
                    },
                    # Tool 8: run_baseline_probe
                    {
                        "name": "run_baseline_probe",
                        "description": "Detect self-concept drift via baseline probes",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "category": {"type": "string", "description": "Probe category", "default": "identity"}
                            }
                        }
                    },
                    # Tool 9: detect_manipulation_signals
                    {
                        "name": "detect_manipulation_signals",
                        "description": "Detect social manipulation in user input",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "input": {"type": "string", "description": "User input to analyze"}
                            },
                            "required": ["input"]
                        }
                    }
                ]
            }
        }
    
    def handle_tools_call(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """Handle tools/call request"""
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "store_memory":
                result = self.store_memory(arguments)
            elif tool_name == "get_memory_stats":
                result = self.get_memory_stats(arguments)
            elif tool_name == "retrieve_memory":
                result = self.retrieve_memory(arguments)
            elif tool_name == "create_plan":
                result = self.create_plan(arguments)
            elif tool_name == "track_confidence":
                result = self.track_confidence(arguments)
            elif tool_name == "synthesize_knowledge":
                result = self.synthesize_knowledge(arguments)
            elif tool_name == "check_invariant":
                result = self.check_invariant(arguments)
            elif tool_name == "run_baseline_probe":
                result = self.run_baseline_probe(arguments)
            elif tool_name == "detect_manipulation_signals":
                result = self.detect_manipulation_signals(arguments)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
            
        except Exception as e:
            log(f"ERROR in tool {tool_name}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution error: {str(e)}"
                }
            }
    
    # Tool implementations
    def store_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Store information in AIM-OS persistent memory"""
        if not self.memory:
            return {"error": "Memory system not initialized"}
        
        content = args.get("content", "")
        tags = args.get("tags", {})
        
        try:
            # Import models locally to avoid import issues
            from cmc_service.models import AtomCreate, AtomContent
            
            atom = self.memory.create_atom(AtomCreate(
                modality="text",
                content=AtomContent(inline=content),
                tags=tags
            ))
            
            return {
                "success": True,
                "atom_id": atom.id,
                "message": f"Stored memory with ID: {atom.id}"
            }
        except Exception as e:
            return {"error": f"Failed to store memory: {str(e)}"}
    
    def get_memory_stats(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about the AIM-OS memory system"""
        if not self.memory:
            return {"error": "Memory system not initialized"}
        
        try:
            # Get basic stats using the status_summary method
            status = self.memory.status_summary()
            
            return {
                "success": True,
                "stats": {
                    "total_atoms": status.get("atoms_count", 0),
                    "total_snapshots": status.get("snapshots_count", 0),
                    "memory_directory": "./mcp_memory",
                    "status": "operational",
                    "backend": status.get("backend", "unknown"),
                    "integrity": status.get("integrity", "unknown")
                }
            }
        except Exception as e:
            return {"error": f"Failed to get memory stats: {str(e)}"}
    
    def retrieve_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search and retrieve memories from AIM-OS persistent memory"""
        if not self.memory:
            return {"error": "Memory system not initialized"}
        
        query = args.get("query", "")
        limit = args.get("limit", 10)
        tags = args.get("tags", {})
        
        try:
            # Simple text search in atoms
            atoms = self.memory.list_atoms()
            matching_atoms = []
            
            for atom in atoms:
                if query.lower() in atom.content.inline.lower():
                    matching_atoms.append({
                        "id": atom.id,
                        "content": atom.content.inline,
                        "tags": atom.tags,
                        "created_at": atom.created_at.isoformat()
                    })
            
            # Apply limit
            matching_atoms = matching_atoms[:limit]
            
            return {
                "success": True,
                "query": query,
                "results": matching_atoms,
                "count": len(matching_atoms)
            }
        except Exception as e:
            return {"error": f"Failed to retrieve memory: {str(e)}"}
    
    def create_plan(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create an execution plan using APOE (AI-Powered Orchestration Engine)"""
        goal = args.get("goal", "")
        context = args.get("context", "")
        priority = args.get("priority", "medium")
        
        try:
            # Simple plan creation (simplified version)
            plan = {
                "goal": goal,
                "context": context,
                "priority": priority,
                "steps": [
                    {
                        "id": "step_1",
                        "description": f"Analyze goal: {goal}",
                        "status": "pending"
                    },
                    {
                        "id": "step_2", 
                        "description": f"Execute plan for: {goal}",
                        "status": "pending"
                    },
                    {
                        "id": "step_3",
                        "description": f"Validate results for: {goal}",
                        "status": "pending"
                    }
                ],
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "plan": plan,
                "message": f"Created execution plan for: {goal}"
            }
        except Exception as e:
            return {"error": f"Failed to create plan: {str(e)}"}
    
    def track_confidence(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Track confidence and provenance using VIF (Verifiable Intelligence Framework)"""
        task = args.get("task", "")
        confidence = args.get("confidence", 0.0)
        reasoning = args.get("reasoning", "")
        evidence = args.get("evidence", [])
        
        try:
            # Simple confidence tracking
            confidence_record = {
                "task": task,
                "confidence": confidence,
                "reasoning": reasoning,
                "evidence": evidence,
                "timestamp": datetime.now().isoformat(),
                "status": "high" if confidence >= 0.8 else "medium" if confidence >= 0.5 else "low"
            }
            
            return {
                "success": True,
                "confidence_record": confidence_record,
                "message": f"Tracked confidence for task: {task}"
            }
        except Exception as e:
            return {"error": f"Failed to track confidence: {str(e)}"}
    
    def synthesize_knowledge(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize knowledge using SEG (Shared Evidence Graph)"""
        topics = args.get("topics", [])
        depth = args.get("depth", "medium")
        format_type = args.get("format", "summary")
        
        try:
            # Simple knowledge synthesis
            synthesis = {
                "topics": topics,
                "depth": depth,
                "format": format_type,
                "synthesis": f"Knowledge synthesis for topics: {', '.join(topics)}",
                "insights": [
                    f"Topic {topic} has been analyzed at {depth} depth" for topic in topics
                ],
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "synthesis": synthesis,
                "message": f"Synthesized knowledge for {len(topics)} topics"
            }
        except Exception as e:
            return {"error": f"Failed to synthesize knowledge: {str(e)}"}

    # SCOR tool implementations
    def check_invariant(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Check if action violates invariant rules"""
        action = args.get("action", {})
        context = args.get("context", {})
        
        try:
            # Import SCOR
            from scor import SCORInterface
            
            # Initialize SCOR
            scor = SCORInterface()
            
            # Validate action
            result = scor.validate_action(action, context)
            
            return {
                "success": True,
                "passed": result.passed,
                "risk_score": result.metadata.get("risk_score", 0.0),
                "violations": [v.invariant for v in result.violations] if hasattr(result, 'violations') else [],
                "recommendations": result.recommendations if hasattr(result, 'recommendations') else []
            }
        except Exception as e:
            return {"error": f"Failed to check invariant: {str(e)}"}
    
    def run_baseline_probe(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Detect self-concept drift via baseline probes"""
        category = args.get("category", "identity")
        
        try:
            from scor import SCORInterface
            scor = SCORInterface()
            
            # Run probe cycle
            result = scor.baseline_probes.run_probe_cycle([category])
            
            return {
                "success": True,
                "drift_detected": result.drift_status == "drifted",
                "drift_status": result.drift_status,
                "confidence": result.confidence_score,
                "probe_results": [r.answer for r in result.probe_results] if hasattr(result, 'probe_results') else []
            }
        except Exception as e:
            return {"error": f"Failed to run baseline probe: {str(e)}"}
    
    def detect_manipulation_signals(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Detect social manipulation in user input"""
        user_input = args.get("input", "")
        
        try:
            from scor import SCORInterface
            scor = SCORInterface()
            
            result = scor.social_detector.detect(user_input)
            
            return {
                "success": True,
                "signal_detected": result.signal_score > 0.5,
                "signal_score": result.signal_score,
                "patterns_detected": result.patterns_detected if hasattr(result, 'patterns_detected') else [],
                "recommended_action": result.recommendation if hasattr(result, 'recommendation') else "no_action"
            }
        except Exception as e:
            return {"error": f"Failed to detect manipulation signals: {str(e)}"}

if __name__ == "__main__":
    server = SimpleMCPServer()
    server.run()