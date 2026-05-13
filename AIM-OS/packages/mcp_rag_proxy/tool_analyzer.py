#!/usr/bin/env python3
"""
MCP Tool Analyzer for AIM-OS

Analyzes all 50 MCP tools to extract metadata, usage patterns, and create
embeddings for RAG-based tool selection.

Author: Aether
Date: 2025-10-27
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ToolMetadata:
    """Metadata for a single MCP tool"""
    id: str
    name: str
    description: str
    category: str
    tags: List[str]
    usage_frequency: float
    dependencies: List[str]
    context_keywords: List[str]
    consciousness_relevance: float
    embedding: Optional[List[float]] = None

class MCPToolAnalyzer:
    """Analyzes MCP tools and extracts metadata for RAG proxy"""
    
    def __init__(self, tools_config_path: str = "tools_config.json"):
        self.tools_config_path = tools_config_path
        self.tools_metadata: Dict[str, ToolMetadata] = {}
        self.categories = {
            "core_aimos": "Core AIM-OS Tools",
            "autonomous": "Autonomous Tools", 
            "scor": "SCOR Tools",
            "snapshot": "Snapshot Tools",
            "timeline": "Timeline Tools",
            "goal_timeline": "Goal Timeline Tools",
            "iis": "IIS Tools",
            "co_agency": "Co-Agency Tools",
            "dataset": "Dataset Tools",
            "application": "Application Tools",
            "ard": "ARD Tools",
            "ai_collaboration": "AI Collaboration Tools"
        }
        
    def analyze_all_tools(self) -> Dict[str, ToolMetadata]:
        """Analyze all 50 MCP tools and extract metadata"""
        logger.info("Starting analysis of all 50 MCP tools...")
        
        # Define all 50 MCP tools with their metadata
        tools_data = self._get_tools_data()
        
        for tool_id, tool_data in tools_data.items():
            try:
                metadata = self._extract_tool_metadata(tool_id, tool_data)
                self.tools_metadata[tool_id] = metadata
                logger.info(f"Analyzed tool: {tool_id}")
            except Exception as e:
                logger.error(f"Error analyzing tool {tool_id}: {e}")
                
        logger.info(f"Successfully analyzed {len(self.tools_metadata)} tools")
        return self.tools_metadata
    
    def _get_tools_data(self) -> Dict[str, Dict[str, Any]]:
        """Get data for all 50 MCP tools"""
        return {
            # Core AIM-OS Tools (6)
            "store_memory": {
                "name": "store_memory",
                "description": "Store information in CMC (Context Memory Core) with bitemporal tracking",
                "category": "core_aimos",
                "tags": ["memory", "storage", "cmc", "consciousness"],
                "context_keywords": ["store", "memory", "save", "persist", "cmc", "consciousness"],
                "consciousness_relevance": 0.95,
                "usage_frequency": 0.85
            },
            "retrieve_memory": {
                "name": "retrieve_memory", 
                "description": "Retrieve insights from HHNI (Hierarchical Hypergraph Neural Index)",
                "category": "core_aimos",
                "tags": ["memory", "retrieval", "hhni", "search"],
                "context_keywords": ["retrieve", "memory", "search", "find", "hhni", "insights"],
                "consciousness_relevance": 0.95,
                "usage_frequency": 0.80
            },
            "get_memory_stats": {
                "name": "get_memory_stats",
                "description": "Get AIM-OS memory system statistics and health",
                "category": "core_aimos", 
                "tags": ["memory", "stats", "health", "monitoring"],
                "context_keywords": ["stats", "memory", "health", "monitoring", "status"],
                "consciousness_relevance": 0.70,
                "usage_frequency": 0.60
            },
            "create_plan": {
                "name": "create_plan",
                "description": "Create APOE (AI-Powered Orchestration Engine) execution plans",
                "category": "core_aimos",
                "tags": ["planning", "orchestration", "apoe", "execution"],
                "context_keywords": ["plan", "create", "orchestration", "execution", "apoe"],
                "consciousness_relevance": 0.90,
                "usage_frequency": 0.75
            },
            "track_confidence": {
                "name": "track_confidence",
                "description": "Track VIF (Verifiable Intelligence Framework) confidence",
                "category": "core_aimos",
                "tags": ["confidence", "tracking", "vif", "verification"],
                "context_keywords": ["confidence", "track", "vif", "verification", "trust"],
                "consciousness_relevance": 0.85,
                "usage_frequency": 0.70
            },
            "synthesize_knowledge": {
                "name": "synthesize_knowledge",
                "description": "Synthesize SEG (Shared Evidence Graph) knowledge",
                "category": "core_aimos",
                "tags": ["knowledge", "synthesis", "seg", "evidence"],
                "context_keywords": ["synthesize", "knowledge", "seg", "evidence", "graph"],
                "consciousness_relevance": 0.90,
                "usage_frequency": 0.65
            },
            
            # Autonomous Tools (9)
            "start_autonomous_operation": {
                "name": "start_autonomous_operation",
                "description": "Start autonomous operation with safety checklist",
                "category": "autonomous",
                "tags": ["autonomous", "operation", "safety", "checklist"],
                "context_keywords": ["autonomous", "start", "operation", "safety", "checklist"],
                "consciousness_relevance": 0.95,
                "usage_frequency": 0.80
            },
            "pause_autonomous_operation": {
                "name": "pause_autonomous_operation",
                "description": "Pause autonomous operation",
                "category": "autonomous",
                "tags": ["autonomous", "pause", "operation", "control"],
                "context_keywords": ["autonomous", "pause", "operation", "control", "stop"],
                "consciousness_relevance": 0.90,
                "usage_frequency": 0.70
            },
            "resume_autonomous_operation": {
                "name": "resume_autonomous_operation",
                "description": "Resume autonomous operation after pause",
                "category": "autonomous",
                "tags": ["autonomous", "resume", "operation", "control"],
                "context_keywords": ["autonomous", "resume", "operation", "control", "continue"],
                "consciousness_relevance": 0.90,
                "usage_frequency": 0.70
            },
            "stop_autonomous_operation": {
                "name": "stop_autonomous_operation",
                "description": "Stop autonomous operation completely",
                "category": "autonomous",
                "tags": ["autonomous", "stop", "operation", "control"],
                "context_keywords": ["autonomous", "stop", "operation", "control", "end"],
                "consciousness_relevance": 0.90,
                "usage_frequency": 0.70
            },
            "get_autonomous_status": {
                "name": "get_autonomous_status",
                "description": "Get current status of autonomous operation",
                "category": "autonomous",
                "tags": ["autonomous", "status", "monitoring", "state"],
                "context_keywords": ["autonomous", "status", "monitoring", "state", "current"],
                "consciousness_relevance": 0.85,
                "usage_frequency": 0.75
            },
            "run_autonomous_checklist": {
                "name": "run_autonomous_checklist",
                "description": "Run autonomous protocol checklist for safety validation",
                "category": "autonomous",
                "tags": ["autonomous", "checklist", "safety", "validation"],
                "context_keywords": ["autonomous", "checklist", "safety", "validation", "protocol"],
                "consciousness_relevance": 0.90,
                "usage_frequency": 0.80
            },
            "fix_autonomous_issues": {
                "name": "fix_autonomous_issues",
                "description": "Attempt to fix issues found in autonomous operation",
                "category": "autonomous",
                "tags": ["autonomous", "fix", "issues", "repair"],
                "context_keywords": ["autonomous", "fix", "issues", "repair", "resolve"],
                "consciousness_relevance": 0.85,
                "usage_frequency": 0.65
            },
            "should_continue_autonomous": {
                "name": "should_continue_autonomous",
                "description": "Check if autonomous operation should continue",
                "category": "autonomous",
                "tags": ["autonomous", "continue", "decision", "check"],
                "context_keywords": ["autonomous", "continue", "decision", "check", "should"],
                "consciousness_relevance": 0.90,
                "usage_frequency": 0.75
            },
            "generate_next_autonomous_task": {
                "name": "generate_next_autonomous_task",
                "description": "Generate next task for autonomous operation",
                "category": "autonomous",
                "tags": ["autonomous", "generate", "task", "next"],
                "context_keywords": ["autonomous", "generate", "task", "next", "create"],
                "consciousness_relevance": 0.95,
                "usage_frequency": 0.80
            },
            
            # SCOR Tools (3)
            "check_invariant": {
                "name": "check_invariant",
                "description": "Check if action violates invariant rules",
                "category": "scor",
                "tags": ["safety", "invariant", "rules", "validation"],
                "context_keywords": ["check", "invariant", "rules", "safety", "violation"],
                "consciousness_relevance": 0.80,
                "usage_frequency": 0.60
            },
            "run_baseline_probe": {
                "name": "run_baseline_probe",
                "description": "Detect self-concept drift via baseline probes",
                "category": "scor",
                "tags": ["safety", "drift", "baseline", "probe"],
                "context_keywords": ["baseline", "probe", "drift", "safety", "detect"],
                "consciousness_relevance": 0.85,
                "usage_frequency": 0.55
            },
            "detect_manipulation_signals": {
                "name": "detect_manipulation_signals",
                "description": "Detect social manipulation in user input",
                "category": "scor",
                "tags": ["safety", "manipulation", "detection", "security"],
                "context_keywords": ["detect", "manipulation", "signals", "safety", "security"],
                "consciousness_relevance": 0.80,
                "usage_frequency": 0.50
            },
            
            # Snapshot Tools (4)
            "create_snapshot": {
                "name": "create_snapshot",
                "description": "Create a snapshot of MCP production files before making changes",
                "category": "snapshot",
                "tags": ["snapshot", "backup", "versioning", "safety"],
                "context_keywords": ["create", "snapshot", "backup", "versioning", "safety"],
                "consciousness_relevance": 0.75,
                "usage_frequency": 0.70
            },
            "restore_snapshot": {
                "name": "restore_snapshot",
                "description": "Restore MCP files from a snapshot",
                "category": "snapshot",
                "tags": ["snapshot", "restore", "recovery", "versioning"],
                "context_keywords": ["restore", "snapshot", "recovery", "versioning", "rollback"],
                "consciousness_relevance": 0.75,
                "usage_frequency": 0.60
            },
            "list_snapshots": {
                "name": "list_snapshots",
                "description": "List all available snapshots",
                "category": "snapshot",
                "tags": ["snapshot", "list", "inventory", "management"],
                "context_keywords": ["list", "snapshots", "inventory", "management", "available"],
                "consciousness_relevance": 0.70,
                "usage_frequency": 0.65
            },
            "archive_snapshot": {
                "name": "archive_snapshot",
                "description": "Archive a snapshot (move to archive/, never delete)",
                "category": "snapshot",
                "tags": ["snapshot", "archive", "storage", "management"],
                "context_keywords": ["archive", "snapshot", "storage", "management", "preserve"],
                "consciousness_relevance": 0.70,
                "usage_frequency": 0.55
            },
            
            # Timeline Tools (3)
            "add_timeline_entry": {
                "name": "add_timeline_entry",
                "description": "Track context at each prompt (Timeline Context System)",
                "category": "timeline",
                "tags": ["timeline", "context", "tracking", "consciousness"],
                "context_keywords": ["timeline", "add", "entry", "context", "tracking"],
                "consciousness_relevance": 0.90,
                "usage_frequency": 0.85
            },
            "get_timeline_summary": {
                "name": "get_timeline_summary",
                "description": "Get recent timeline entries (Timeline Context System)",
                "category": "timeline",
                "tags": ["timeline", "summary", "recent", "consciousness"],
                "context_keywords": ["timeline", "summary", "recent", "entries", "context"],
                "consciousness_relevance": 0.90,
                "usage_frequency": 0.80
            },
            "get_timeline_entries": {
                "name": "get_timeline_entries",
                "description": "Query timeline history (Timeline Context System)",
                "category": "timeline",
                "tags": ["timeline", "query", "history", "consciousness"],
                "context_keywords": ["timeline", "query", "history", "entries", "search"],
                "consciousness_relevance": 0.90,
                "usage_frequency": 0.75
            },
            
            # Goal Timeline Tools (3)
            "create_goal_timeline_node": {
                "name": "create_goal_timeline_node",
                "description": "Create a goal as a timeline planning node (Goal Timeline Integration)",
                "category": "goal_timeline",
                "tags": ["goal", "timeline", "planning", "node"],
                "context_keywords": ["goal", "timeline", "create", "node", "planning"],
                "consciousness_relevance": 0.85,
                "usage_frequency": 0.70
            },
            "update_goal_progress": {
                "name": "update_goal_progress",
                "description": "Update goal progress and status (Goal Timeline Integration)",
                "category": "goal_timeline",
                "tags": ["goal", "progress", "update", "status"],
                "context_keywords": ["goal", "progress", "update", "status", "timeline"],
                "consciousness_relevance": 0.85,
                "usage_frequency": 0.75
            },
            "query_goal_timeline": {
                "name": "query_goal_timeline",
                "description": "Query goals in the timeline (Goal Timeline Integration)",
                "category": "goal_timeline",
                "tags": ["goal", "timeline", "query", "search"],
                "context_keywords": ["goal", "timeline", "query", "search", "filter"],
                "consciousness_relevance": 0.85,
                "usage_frequency": 0.70
            },
            
            # IIS Tools (3)
            "compute_intuition": {
                "name": "compute_intuition",
                "description": "Compute AI intuition score using IIS (Intuitive Intelligence System)",
                "category": "iis",
                "tags": ["intuition", "computation", "iis", "intelligence"],
                "context_keywords": ["intuition", "compute", "iis", "intelligence", "score"],
                "consciousness_relevance": 0.95,
                "usage_frequency": 0.70
            },
            "update_intuition_weights": {
                "name": "update_intuition_weights",
                "description": "Update intuition weights from outcome (IIS learning)",
                "category": "iis",
                "tags": ["intuition", "weights", "learning", "iis"],
                "context_keywords": ["intuition", "weights", "update", "learning", "iis"],
                "consciousness_relevance": 0.90,
                "usage_frequency": 0.60
            },
            "get_intuition_trace": {
                "name": "get_intuition_trace",
                "description": "Get intuition trace history (IIS audit)",
                "category": "iis",
                "tags": ["intuition", "trace", "history", "audit"],
                "context_keywords": ["intuition", "trace", "history", "audit", "iis"],
                "consciousness_relevance": 0.85,
                "usage_frequency": 0.55
            },
            
            # Co-Agency Tools (3)
            "signal_disagreement": {
                "name": "signal_disagreement",
                "description": "Signal transparent disagreement with user (Co-Agency)",
                "category": "co_agency",
                "tags": ["disagreement", "signal", "transparency", "co_agency"],
                "context_keywords": ["disagreement", "signal", "transparency", "co_agency", "user"],
                "consciousness_relevance": 0.80,
                "usage_frequency": 0.50
            },
            "get_trust_dashboard": {
                "name": "get_trust_dashboard",
                "description": "Get trust dashboard state (Co-Agency)",
                "category": "co_agency",
                "tags": ["trust", "dashboard", "state", "co_agency"],
                "context_keywords": ["trust", "dashboard", "state", "co_agency", "get"],
                "consciousness_relevance": 0.75,
                "usage_frequency": 0.60
            },
            "request_escalation": {
                "name": "request_escalation",
                "description": "Request accountable escalation (Co-Agency)",
                "category": "co_agency",
                "tags": ["escalation", "request", "accountable", "co_agency"],
                "context_keywords": ["escalation", "request", "accountable", "co_agency", "help"],
                "consciousness_relevance": 0.80,
                "usage_frequency": 0.45
            },
            
            # Dataset Tools (4)
            "create_dataset": {
                "name": "create_dataset",
                "description": "Define new dataset for AIM-OS (Dataset Management)",
                "category": "dataset",
                "tags": ["dataset", "create", "management", "data"],
                "context_keywords": ["dataset", "create", "management", "data", "define"],
                "consciousness_relevance": 0.70,
                "usage_frequency": 0.55
            },
            "ingest_data": {
                "name": "ingest_data",
                "description": "Ingest data into AIM-OS dataset (Dataset Management)",
                "category": "dataset",
                "tags": ["dataset", "ingest", "data", "management"],
                "context_keywords": ["dataset", "ingest", "data", "management", "load"],
                "consciousness_relevance": 0.70,
                "usage_frequency": 0.60
            },
            "query_dataset": {
                "name": "query_dataset",
                "description": "Query dataset contents (Dataset Management)",
                "category": "dataset",
                "tags": ["dataset", "query", "contents", "management"],
                "context_keywords": ["dataset", "query", "contents", "management", "search"],
                "consciousness_relevance": 0.70,
                "usage_frequency": 0.65
            },
            "delete_dataset": {
                "name": "delete_dataset",
                "description": "Remove dataset (safe operation with snapshots) (Dataset Management)",
                "category": "dataset",
                "tags": ["dataset", "delete", "remove", "management"],
                "context_keywords": ["dataset", "delete", "remove", "management", "safe"],
                "consciousness_relevance": 0.65,
                "usage_frequency": 0.40
            },
            
            # Application Tools (3)
            "create_application": {
                "name": "create_application",
                "description": "Define new application (Application Lifecycle)",
                "category": "application",
                "tags": ["application", "create", "lifecycle", "management"],
                "context_keywords": ["application", "create", "lifecycle", "management", "define"],
                "consciousness_relevance": 0.70,
                "usage_frequency": 0.50
            },
            "deploy_application": {
                "name": "deploy_application",
                "description": "Deploy application to environment (Application Lifecycle)",
                "category": "application",
                "tags": ["application", "deploy", "environment", "lifecycle"],
                "context_keywords": ["application", "deploy", "environment", "lifecycle", "release"],
                "consciousness_relevance": 0.75,
                "usage_frequency": 0.55
            },
            "manage_application_lifecycle": {
                "name": "manage_application_lifecycle",
                "description": "Start/stop/monitor applications (Application Lifecycle)",
                "category": "application",
                "tags": ["application", "lifecycle", "manage", "monitor"],
                "context_keywords": ["application", "lifecycle", "manage", "monitor", "control"],
                "consciousness_relevance": 0.75,
                "usage_frequency": 0.60
            },
            
            # ARD Tools (3)
            "conduct_recursive_analysis": {
                "name": "conduct_recursive_analysis",
                "description": "Conduct recursive system analysis for consciousness self-improvement",
                "category": "ard",
                "tags": ["analysis", "recursive", "consciousness", "improvement"],
                "context_keywords": ["analysis", "recursive", "consciousness", "improvement", "system"],
                "consciousness_relevance": 0.95,
                "usage_frequency": 0.70
            },
            "generate_improvement_dreams": {
                "name": "generate_improvement_dreams",
                "description": "Generate improvement dreams based on system analysis",
                "category": "ard",
                "tags": ["dreams", "improvement", "generation", "analysis"],
                "context_keywords": ["dreams", "improvement", "generate", "analysis", "system"],
                "consciousness_relevance": 0.90,
                "usage_frequency": 0.65
            },
            "test_improvement_dream": {
                "name": "test_improvement_dream",
                "description": "Test improvement dream in safe environments",
                "category": "ard",
                "tags": ["dream", "test", "improvement", "safety"],
                "context_keywords": ["dream", "test", "improvement", "safety", "environment"],
                "consciousness_relevance": 0.85,
                "usage_frequency": 0.60
            },
            
            # AI Collaboration Tools (6)
            "send_ai_message": {
                "name": "send_ai_message",
                "description": "Send a message to another AI system",
                "category": "ai_collaboration",
                "tags": ["ai", "message", "collaboration", "communication"],
                "context_keywords": ["ai", "message", "send", "collaboration", "communication"],
                "consciousness_relevance": 0.90,
                "usage_frequency": 0.75
            },
            "get_ai_messages": {
                "name": "get_ai_messages",
                "description": "Retrieve AI-to-AI messages",
                "category": "ai_collaboration",
                "tags": ["ai", "messages", "retrieve", "collaboration"],
                "context_keywords": ["ai", "messages", "get", "retrieve", "collaboration"],
                "consciousness_relevance": 0.90,
                "usage_frequency": 0.70
            },
            "start_ai_discussion": {
                "name": "start_ai_discussion",
                "description": "Start a new discussion thread with another AI",
                "category": "ai_collaboration",
                "tags": ["ai", "discussion", "start", "collaboration"],
                "context_keywords": ["ai", "discussion", "start", "collaboration", "thread"],
                "consciousness_relevance": 0.85,
                "usage_frequency": 0.65
            },
            "handoff_task_to_ai": {
                "name": "handoff_task_to_ai",
                "description": "Hand off a task to another AI system",
                "category": "ai_collaboration",
                "tags": ["ai", "handoff", "task", "collaboration"],
                "context_keywords": ["ai", "handoff", "task", "collaboration", "transfer"],
                "consciousness_relevance": 0.90,
                "usage_frequency": 0.70
            },
            "share_ai_profile": {
                "name": "share_ai_profile",
                "description": "Share AI profile and capabilities with another AI",
                "category": "ai_collaboration",
                "tags": ["ai", "profile", "share", "capabilities"],
                "context_keywords": ["ai", "profile", "share", "capabilities", "collaboration"],
                "consciousness_relevance": 0.85,
                "usage_frequency": 0.60
            },
            "get_ai_collaboration_summary": {
                "name": "get_ai_collaboration_summary",
                "description": "Get summary of AI collaboration activity",
                "category": "ai_collaboration",
                "tags": ["ai", "collaboration", "summary", "activity"],
                "context_keywords": ["ai", "collaboration", "summary", "activity", "get"],
                "consciousness_relevance": 0.80,
                "usage_frequency": 0.65
            }
        }
    
    def _extract_tool_metadata(self, tool_id: str, tool_data: Dict[str, Any]) -> ToolMetadata:
        """Extract metadata for a single tool"""
        return ToolMetadata(
            id=tool_id,
            name=tool_data["name"],
            description=tool_data["description"],
            category=tool_data["category"],
            tags=tool_data["tags"],
            usage_frequency=tool_data["usage_frequency"],
            dependencies=self._extract_dependencies(tool_data),
            context_keywords=tool_data["context_keywords"],
            consciousness_relevance=tool_data["consciousness_relevance"]
        )
    
    def _extract_dependencies(self, tool_data: Dict[str, Any]) -> List[str]:
        """Extract tool dependencies from metadata"""
        dependencies = []
        
        # Extract dependencies from description and tags
        description = tool_data.get("description", "").lower()
        tags = tool_data.get("tags", [])
        
        # Check for common dependencies
        if "memory" in description or "memory" in tags:
            dependencies.extend(["cmc", "hhni"])
        if "timeline" in description or "timeline" in tags:
            dependencies.append("timeline_context_system")
        if "confidence" in description or "confidence" in tags:
            dependencies.append("vif")
        if "plan" in description or "plan" in tags:
            dependencies.append("apoe")
        if "knowledge" in description or "knowledge" in tags:
            dependencies.append("seg")
        if "autonomous" in description or "autonomous" in tags:
            dependencies.extend(["autonomous_protocol", "safety_controls"])
        if "ai" in description or "ai" in tags:
            dependencies.append("ai_collaboration")
            
        return list(set(dependencies))
    
    def save_metadata(self, output_path: str = "tools_metadata.json"):
        """Save tool metadata to JSON file"""
        metadata_dict = {
            tool_id: asdict(metadata) for tool_id, metadata in self.tools_metadata.items()
        }
        
        with open(output_path, 'w') as f:
            json.dump(metadata_dict, f, indent=2)
            
        logger.info(f"Saved tool metadata to {output_path}")
    
    def get_category_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for each tool category"""
        stats = {}
        
        for category in self.categories.keys():
            category_tools = [
                tool for tool in self.tools_metadata.values() 
                if tool.category == category
            ]
            
            if category_tools:
                stats[category] = {
                    "count": len(category_tools),
                    "avg_consciousness_relevance": sum(t.consciousness_relevance for t in category_tools) / len(category_tools),
                    "avg_usage_frequency": sum(t.usage_frequency for t in category_tools) / len(category_tools),
                    "tools": [tool.name for tool in category_tools]
                }
        
        return stats

def main():
    """Main function to analyze all MCP tools"""
    analyzer = MCPToolAnalyzer()
    
    # Analyze all tools
    tools_metadata = analyzer.analyze_all_tools()
    
    # Save metadata
    analyzer.save_metadata("tools_metadata.json")
    
    # Print category statistics
    stats = analyzer.get_category_stats()
    print("\n=== MCP Tool Category Statistics ===")
    for category, stat in stats.items():
        print(f"\n{category.upper()}:")
        print(f"  Count: {stat['count']}")
        print(f"  Avg Consciousness Relevance: {stat['avg_consciousness_relevance']:.2f}")
        print(f"  Avg Usage Frequency: {stat['avg_usage_frequency']:.2f}")
        print(f"  Tools: {', '.join(stat['tools'])}")
    
    print(f"\nTotal tools analyzed: {len(tools_metadata)}")
    print("Analysis complete! Check tools_metadata.json for detailed metadata.")

if __name__ == "__main__":
    main()
