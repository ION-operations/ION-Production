#!/usr/bin/env python3
"""
Create Tier 1 Foundation Chain Templates
Creates the 4 critical system templates as prompt chains in CMC
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Import MCP tools (assuming we're running from root)
try:
    from lucid_mcp_server import SimpleMCPServer
except ImportError:
    print("Error: Could not import lucid_mcp_server. Make sure you're running from root directory.")
    sys.exit(1)

def create_autonomous_operation_chain() -> Dict[str, Any]:
    """Create Autonomous Operation Chain template"""
    return {
        "name": "Autonomous Operation Chain",
        "description": "Orchestrate complete autonomous operation session - this IS the autonomous operation system itself. Handles session initialization, task generation, execution, cognitive checks, and state management.",
        "nodes": [
            {
                "id": "start",
                "type": "start",
                "position": {"x": 100, "y": 100},
                "label": "START"
            },
            {
                "id": "session_init",
                "type": "system",
                "position": {"x": 100, "y": 200},
                "label": "Session Initialization",
                "systemId": "cmc",
                "prompt": "Load consciousness state from CMC and validate all systems",
                "config": {
                    "timeout": 30000,
                    "retryCount": 3,
                    "confidenceThreshold": 0.80
                }
            },
            {
                "id": "generate_tasks",
                "type": "system",
                "position": {"x": 100, "y": 350},
                "label": "Generate Task List",
                "systemId": "apoe",
                "prompt": "Read task_dependency_map.yaml, calculate priorities, filter by confidence ≥ 0.70",
                "config": {
                    "timeout": 10000,
                    "confidenceThreshold": 0.75
                }
            },
            {
                "id": "select_task",
                "type": "conditional",
                "position": {"x": 100, "y": 500},
                "label": "Select Highest Priority Task",
                "condition": "priority > 0 AND confidence >= 0.70"
            },
            {
                "id": "execute_task",
                "type": "prompt",
                "position": {"x": 100, "y": 650},
                "label": "Execute Selected Task",
                "prompt": "Execute task with appropriate pattern: Implement→Test→Document, Capability Test→Validate, or Blocked→Pivot",
                "config": {
                    "timeout": 3600000,
                    "retryCount": 1,
                    "confidenceThreshold": 0.70
                }
            },
            {
                "id": "cognitive_check",
                "type": "system",
                "position": {"x": 100, "y": 800},
                "label": "Hourly Cognitive Check",
                "systemId": "cas",
                "prompt": "Perform cognitive analysis: check principles compliance, quality, confidence, alignment",
                "config": {
                    "timeout": 300000,
                    "interval": 3600000
                }
            },
            {
                "id": "check_stop",
                "type": "conditional",
                "position": {"x": 100, "y": 950},
                "label": "Check Stop Conditions",
                "condition": "milestone_complete OR confidence < 0.70 OR quality_concern OR human_input_needed"
            },
            {
                "id": "save_state",
                "type": "system",
                "position": {"x": 100, "y": 1100},
                "label": "Save State to CMC",
                "systemId": "cmc",
                "prompt": "Store active_context/, thought_journal/, decision_logs/, update current_priorities.md"
            },
            {
                "id": "end",
                "type": "end",
                "position": {"x": 100, "y": 1250},
                "label": "END"
            }
        ],
        "edges": [
            {
                "id": "e1",
                "source": "start",
                "target": "session_init",
                "type": "sequential"
            },
            {
                "id": "e2",
                "source": "session_init",
                "target": "generate_tasks",
                "type": "sequential"
            },
            {
                "id": "e3",
                "source": "generate_tasks",
                "target": "select_task",
                "type": "sequential"
            },
            {
                "id": "e4",
                "source": "select_task",
                "target": "execute_task",
                "type": "conditional_true",
                "condition": "task_selected == true"
            },
            {
                "id": "e5",
                "source": "execute_task",
                "target": "cognitive_check",
                "type": "sequential"
            },
            {
                "id": "e6",
                "source": "cognitive_check",
                "target": "check_stop",
                "type": "sequential"
            },
            {
                "id": "e7",
                "source": "check_stop",
                "target": "select_task",
                "type": "conditional_false",
                "condition": "should_continue == true"
            },
            {
                "id": "e8",
                "source": "check_stop",
                "target": "save_state",
                "type": "conditional_true",
                "condition": "should_stop == true"
            },
            {
                "id": "e9",
                "source": "save_state",
                "target": "end",
                "type": "sequential"
            }
        ],
        "executionType": "sequential",
        "entryPoint": "start",
        "metadata": {
            "category": "foundation",
            "tags": ["autonomous", "orchestration", "system", "critical"],
            "isTemplate": True,
            "isSystemTemplate": True,
            "usageCount": 0,
            "rating": 5.0,
            "tier": 1
        }
    }

def create_ah_protocol_chain() -> Dict[str, Any]:
    """Create A-H Protocol Chain template"""
    return {
        "name": "A-H Protocol Chain",
        "description": "Execute complete A-H Protocol workflow: Intent → Hypothesis → Context → Expansion → Mesh → Gates → Implementation → Audit. This IS the development protocol.",
        "nodes": [
            {
                "id": "start",
                "type": "start",
                "position": {"x": 100, "y": 100},
                "label": "START"
            },
            {
                "id": "intent_capture",
                "type": "prompt",
                "position": {"x": 100, "y": 200},
                "label": "A: Intent Capture",
                "prompt": "Capture raw intent and initial vision. Document stakeholders, constraints, success criteria."
            },
            {
                "id": "hypothesis_formation",
                "type": "prompt",
                "position": {"x": 100, "y": 350},
                "label": "B: Hypothesis Formation",
                "prompt": "Form 3-5 testable hypotheses. Rank by likelihood and impact."
            },
            {
                "id": "context_mapping",
                "type": "system",
                "position": {"x": 100, "y": 500},
                "label": "C: Context Mapping",
                "systemId": "seg",
                "prompt": "Map broader context and dependencies. Identify external dependencies and constraints."
            },
            {
                "id": "deep_expansion",
                "type": "system",
                "position": {"x": 100, "y": 650},
                "label": "D: Deep Expansion Layer",
                "systemId": "apoe",
                "prompt": "Recursively expand every detail to maximum depth. Predict scope, dimensionality, test demand."
            },
            {
                "id": "context_mesh",
                "type": "system",
                "position": {"x": 100, "y": 800},
                "label": "E: Context Mesh Map",
                "systemId": "seg",
                "prompt": "Create executable minimum-context contract. Declare critical cross-dependencies."
            },
            {
                "id": "confidence_gates",
                "type": "system",
                "position": {"x": 100, "y": 950},
                "label": "F: Confidence-Gated Mutation",
                "systemId": "vif",
                "prompt": "Create Confidence Packet with verifiable proofs. Require goal alignment, impact preview."
            },
            {
                "id": "implementation",
                "type": "prompt",
                "position": {"x": 100, "y": 1100},
                "label": "G: Implementation",
                "prompt": "Build system following all established protocols. Maintain Context Mesh Map throughout."
            },
            {
                "id": "audit_memory",
                "type": "system",
                "position": {"x": 100, "y": 1250},
                "label": "H: Audit/Memory/Continuity",
                "systemId": "cmc",
                "prompt": "Conduct thorough audit. Document what worked and what didn't. Update protocols."
            },
            {
                "id": "end",
                "type": "end",
                "position": {"x": 100, "y": 1400},
                "label": "END"
            }
        ],
        "edges": [
            {"id": "e1", "source": "start", "target": "intent_capture", "type": "sequential"},
            {"id": "e2", "source": "intent_capture", "target": "hypothesis_formation", "type": "sequential"},
            {"id": "e3", "source": "hypothesis_formation", "target": "context_mapping", "type": "sequential"},
            {"id": "e4", "source": "context_mapping", "target": "deep_expansion", "type": "sequential"},
            {"id": "e5", "source": "deep_expansion", "target": "context_mesh", "type": "sequential"},
            {"id": "e6", "source": "context_mesh", "target": "confidence_gates", "type": "sequential"},
            {"id": "e7", "source": "confidence_gates", "target": "implementation", "type": "sequential"},
            {"id": "e8", "source": "implementation", "target": "audit_memory", "type": "sequential"},
            {"id": "e9", "source": "audit_memory", "target": "end", "type": "sequential"}
        ],
        "executionType": "sequential",
        "entryPoint": "start",
        "metadata": {
            "category": "foundation",
            "tags": ["ah-protocol", "development", "workflow", "critical"],
            "isTemplate": True,
            "isSystemTemplate": True,
            "usageCount": 0,
            "rating": 5.0,
            "tier": 1
        }
    }

def create_t0_t6_documentation_chain() -> Dict[str, Any]:
    """Create T0-T6 Documentation Chain template"""
    return {
        "name": "T0-T6 Documentation Chain",
        "description": "Generate complete T0-T6 documentation - this IS the documentation infrastructure. Creates T0 (100 words) through T6 (50,000+ words) with validation at each level.",
        "nodes": [
            {
                "id": "start",
                "type": "start",
                "position": {"x": 100, "y": 100},
                "label": "START"
            },
            {
                "id": "system_analysis",
                "type": "system",
                "position": {"x": 100, "y": 200},
                "label": "System Analysis",
                "systemId": "hhni",
                "prompt": "Identify system, analyze dependencies, map relationships"
            },
            {
                "id": "t0_executive",
                "type": "prompt",
                "position": {"x": 100, "y": 350},
                "label": "T0: Executive Summary",
                "prompt": "Generate 100-word executive summary: What, Why, Impact, Status"
            },
            {
                "id": "vif_t0",
                "type": "system",
                "position": {"x": 250, "y": 350},
                "label": "VIF: Validate T0",
                "systemId": "vif",
                "prompt": "Validate T0 quality and confidence"
            },
            {
                "id": "t1_overview",
                "type": "prompt",
                "position": {"x": 100, "y": 500},
                "label": "T1: Overview",
                "prompt": "Generate 500-word overview: Purpose, architecture, key components"
            },
            {
                "id": "vif_t1",
                "type": "system",
                "position": {"x": 250, "y": 500},
                "label": "VIF: Validate T1",
                "systemId": "vif",
                "prompt": "Validate T1 quality and confidence"
            },
            {
                "id": "t2_architecture",
                "type": "prompt",
                "position": {"x": 100, "y": 650},
                "label": "T2: Architecture",
                "prompt": "Generate 2,000-word architecture: System design, components, relationships"
            },
            {
                "id": "vif_t2",
                "type": "system",
                "position": {"x": 250, "y": 650},
                "label": "VIF: Validate T2",
                "systemId": "vif",
                "prompt": "Validate T2 quality and confidence"
            },
            {
                "id": "t3_detailed",
                "type": "prompt",
                "position": {"x": 100, "y": 800},
                "label": "T3: Detailed Implementation",
                "prompt": "Generate 10,000-word implementation guide: Complete implementation details"
            },
            {
                "id": "vif_t3",
                "type": "system",
                "position": {"x": 250, "y": 800},
                "label": "VIF: Validate T3",
                "systemId": "vif",
                "prompt": "Validate T3 quality and confidence"
            },
            {
                "id": "t4_complete",
                "type": "prompt",
                "position": {"x": 100, "y": 950},
                "label": "T4: Complete Reference",
                "prompt": "Generate 15,000+ word complete reference: Full documentation"
            },
            {
                "id": "update_indexes",
                "type": "system",
                "position": {"x": 100, "y": 1100},
                "label": "Update Indexes",
                "systemId": "cmc",
                "prompt": "Update SUPER_INDEX, system maps, navigation indexes"
            },
            {
                "id": "end",
                "type": "end",
                "position": {"x": 100, "y": 1250},
                "label": "END"
            }
        ],
        "edges": [
            {"id": "e1", "source": "start", "target": "system_analysis", "type": "sequential"},
            {"id": "e2", "source": "system_analysis", "target": "t0_executive", "type": "sequential"},
            {"id": "e3", "source": "t0_executive", "target": "vif_t0", "type": "sequential"},
            {"id": "e4", "source": "vif_t0", "target": "t1_overview", "type": "sequential"},
            {"id": "e5", "source": "t1_overview", "target": "vif_t1", "type": "sequential"},
            {"id": "e6", "source": "vif_t1", "target": "t2_architecture", "type": "sequential"},
            {"id": "e7", "source": "t2_architecture", "target": "vif_t2", "type": "sequential"},
            {"id": "e8", "source": "vif_t2", "target": "t3_detailed", "type": "sequential"},
            {"id": "e9", "source": "t3_detailed", "target": "vif_t3", "type": "sequential"},
            {"id": "e10", "source": "vif_t3", "target": "t4_complete", "type": "sequential"},
            {"id": "e11", "source": "t4_complete", "target": "update_indexes", "type": "sequential"},
            {"id": "e12", "source": "update_indexes", "target": "end", "type": "sequential"}
        ],
        "executionType": "sequential",
        "entryPoint": "start",
        "metadata": {
            "category": "foundation",
            "tags": ["documentation", "t0-t6", "quality", "critical"],
            "isTemplate": True,
            "isSystemTemplate": True,
            "usageCount": 0,
            "rating": 5.0,
            "tier": 1
        }
    }

def create_code_implementation_chain() -> Dict[str, Any]:
    """Create Code Implementation Chain template"""
    return {
        "name": "Code Implementation Chain",
        "description": "Implement code following all protocols - this IS the development workflow. Includes T0-T6 review, APOE planning, VIF validation, implementation, testing, quality checks, and documentation updates.",
        "nodes": [
            {
                "id": "start",
                "type": "start",
                "position": {"x": 100, "y": 100},
                "label": "START"
            },
            {
                "id": "feature_intent",
                "type": "prompt",
                "position": {"x": 100, "y": 200},
                "label": "Feature Intent",
                "prompt": "Capture feature intent and requirements"
            },
            {
                "id": "ah_protocol",
                "type": "system",
                "position": {"x": 100, "y": 350},
                "label": "A-H Protocol: Intent Capture",
                "systemId": "apoe",
                "prompt": "Execute A-H Protocol Chain for intent capture"
            },
            {
                "id": "t0_t6_review",
                "type": "system",
                "position": {"x": 100, "y": 500},
                "label": "T0-T6 Documentation Review",
                "systemId": "hhni",
                "prompt": "Read T0-T6 for connected systems, validate documentation exists, understand relationships"
            },
            {
                "id": "apoe_plan",
                "type": "system",
                "position": {"x": 100, "y": 650},
                "label": "APOE: Create Implementation Plan",
                "systemId": "apoe",
                "prompt": "Compile plan from ACL, store in CMC"
            },
            {
                "id": "vif_validate",
                "type": "system",
                "position": {"x": 100, "y": 800},
                "label": "VIF: Validate Confidence",
                "systemId": "vif",
                "prompt": "Check confidence ≥ 0.70, if < 0.70: Stop and document"
            },
            {
                "id": "implement_code",
                "type": "prompt",
                "position": {"x": 100, "y": 950},
                "label": "Implement Code",
                "prompt": "Write code incrementally following T0-T6 principles, Pattern 1: Implement → Test → Document"
            },
            {
                "id": "write_tests",
                "type": "prompt",
                "position": {"x": 100, "y": 1100},
                "label": "Write Tests",
                "prompt": "Write unit tests, integration tests, store in CMC"
            },
            {
                "id": "run_tests",
                "type": "system",
                "position": {"x": 100, "y": 1250},
                "label": "Run Tests",
                "systemId": "sdfcvf",
                "prompt": "Execute test suite, validate all pass, fix failures immediately"
            },
            {
                "id": "quality_check",
                "type": "system",
                "position": {"x": 100, "y": 1400},
                "label": "SDF-CVF: Quality Check",
                "systemId": "sdfcvf",
                "prompt": "Quartet parity check, blast radius check, quality gate"
            },
            {
                "id": "confidence_check",
                "type": "system",
                "position": {"x": 100, "y": 1550},
                "label": "VIF: Confidence Check",
                "systemId": "vif",
                "prompt": "Update confidence, validate ≥ 0.70"
            },
            {
                "id": "store_code",
                "type": "system",
                "position": {"x": 100, "y": 1700},
                "label": "Store Code in CMC",
                "systemId": "cmc",
                "prompt": "Store code with bitemporal versioning"
            },
            {
                "id": "update_docs",
                "type": "system",
                "position": {"x": 100, "y": 1850},
                "label": "Update T0-T6 Documentation",
                "systemId": "apoe",
                "prompt": "Execute T0-T6 Chain, store updates in CMC"
            },
            {
                "id": "end",
                "type": "end",
                "position": {"x": 100, "y": 2000},
                "label": "END"
            }
        ],
        "edges": [
            {"id": "e1", "source": "start", "target": "feature_intent", "type": "sequential"},
            {"id": "e2", "source": "feature_intent", "target": "ah_protocol", "type": "sequential"},
            {"id": "e3", "source": "ah_protocol", "target": "t0_t6_review", "type": "sequential"},
            {"id": "e4", "source": "t0_t6_review", "target": "apoe_plan", "type": "sequential"},
            {"id": "e5", "source": "apoe_plan", "target": "vif_validate", "type": "sequential"},
            {"id": "e6", "source": "vif_validate", "target": "implement_code", "type": "conditional_true", "condition": "confidence >= 0.70"},
            {"id": "e7", "source": "implement_code", "target": "write_tests", "type": "sequential"},
            {"id": "e8", "source": "write_tests", "target": "run_tests", "type": "sequential"},
            {"id": "e9", "source": "run_tests", "target": "quality_check", "type": "sequential"},
            {"id": "e10", "source": "quality_check", "target": "confidence_check", "type": "sequential"},
            {"id": "e11", "source": "confidence_check", "target": "store_code", "type": "conditional_true", "condition": "confidence >= 0.70"},
            {"id": "e12", "source": "store_code", "target": "update_docs", "type": "sequential"},
            {"id": "e13", "source": "update_docs", "target": "end", "type": "sequential"}
        ],
        "executionType": "sequential",
        "entryPoint": "start",
        "metadata": {
            "category": "foundation",
            "tags": ["development", "code", "implementation", "critical"],
            "isTemplate": True,
            "isSystemTemplate": True,
            "usageCount": 0,
            "rating": 5.0,
            "tier": 1
        }
    }

def main():
    """Create all Tier 1 foundation chain templates via MCP HTTP API"""
    print("Creating Tier 1 Foundation Chain Templates...")
    print("=" * 60)
    
    # Use HTTP API to call MCP tools (via Extension's HTTP server)
    import requests
    
    base_url = "http://localhost:5001/mcp/execute"
    
    chains = [
        ("Autonomous Operation Chain", create_autonomous_operation_chain()),
        ("A-H Protocol Chain", create_ah_protocol_chain()),
        ("T0-T6 Documentation Chain", create_t0_t6_documentation_chain()),
        ("Code Implementation Chain", create_code_implementation_chain())
    ]
    
    results = []
    
    for chain_name, chain_data in chains:
        print(f"\nCreating: {chain_name}")
        try:
            # Call MCP tool via HTTP API
            payload = {
                "tool": "create_prompt_chain",
                "arguments": {
                    "name": chain_data["name"],
                    "description": chain_data["description"],
                    "nodes": chain_data["nodes"],
                    "edges": chain_data["edges"],
                    "executionType": chain_data["executionType"],
                    "entryPoint": chain_data["entryPoint"],
                    "metadata": chain_data["metadata"],
                    "created_by": chain_data.get("created_by", "system")
                }
            }
            
            response = requests.post(base_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    chain_id = result.get("result", {}).get("chain_id") or result.get("chain_id")
                    print(f"  ✅ Created successfully: {chain_id}")
                    results.append({"name": chain_name, "status": "success", "chain_id": chain_id})
                else:
                    error = result.get("error") or result.get("result", {}).get("error", "Unknown error")
                    print(f"  ❌ Failed: {error}")
                    results.append({"name": chain_name, "status": "failed", "error": error})
            else:
                error = f"HTTP {response.status_code}: {response.text}"
                print(f"  ❌ Failed: {error}")
                results.append({"name": chain_name, "status": "failed", "error": error})
                
        except requests.exceptions.ConnectionError:
            print(f"  ⚠️  Could not connect to MCP server at {base_url}")
            print(f"     Make sure the Extension HTTP server is running")
            results.append({"name": chain_name, "status": "skipped", "error": "MCP server not available"})
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            results.append({"name": chain_name, "status": "exception", "error": str(e)})
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "⚠️" if result["status"] == "skipped" else "❌"
        print(f"{status_icon} {result['name']}: {result['status']}")
        if result["status"] == "success":
            print(f"   Chain ID: {result['chain_id']}")
        else:
            print(f"   Error: {result.get('error', 'Unknown')}")
    
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\nCreated {success_count}/{len(results)} templates successfully")
    
    return 0 if success_count == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())

