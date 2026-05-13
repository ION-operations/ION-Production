#!/usr/bin/env python3
"""
Dynamic Cursor Rules Loader System
Intelligently loads and applies Cursor IDE rules based on context and protocol requirements.
"""

import os
import json
import time
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

class ContextType(Enum):
    """Types of context that can trigger rule loading"""
    PROJECT_TYPE = "project_type"
    TASK_TYPE = "task_type"
    PROTOCOL_REQUIRED = "protocol_required"
    SESSION_STATE = "session_state"
    USER_PREFERENCE = "user_preference"
    COMPLEXITY_LEVEL = "complexity_level"

class RulePartition(Enum):
    """Available rule partitions"""
    BASE_RULES = "base_rules"
    L0_L4_PROTOCOL = "l0_l4_protocol"
    AH_PROTOCOL = "ah_protocol"
    MCP_TOOLS = "mcp_tools"
    QUALITY_STANDARDS = "quality_standards"
    TESTING_PROTOCOLS = "testing_protocols"
    DOCUMENTATION_STANDARDS = "documentation_standards"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    CONSCIOUSNESS_MEMORY = "consciousness_memory"
    PLANNING_GOALS = "planning_goals"
    SUPPORTING_STANDARDS = "supporting_standards"
    ENHANCED_FOUNDATIONAL = "enhanced_foundational"

@dataclass
class ContextProfile:
    """Profile of current context for rule selection"""
    project_type: str = "aim_os"  # aim_os, general, documentation, testing
    task_type: str = "development"  # development, documentation, testing, debugging
    protocol_required: List[str] = None  # l0_l4, ah_protocol, lucid, etc.
    session_state: str = "active"  # active, paused, debugging, emergency
    user_preference: str = "standard"  # standard, minimal, comprehensive
    confidence_level: float = 0.8  # 0.0 to 1.0
    complexity_level: str = "medium"  # low, medium, high, critical
    
    def __post_init__(self):
        if self.protocol_required is None:
            self.protocol_required = []

@dataclass
class RuleMetadata:
    """Metadata for a rule partition"""
    name: str
    description: str
    priority: int  # 1-10, higher = more important
    dependencies: List[str]  # Other partitions this depends on
    conflicts: List[str]  # Partitions this conflicts with
    context_requirements: Dict[ContextType, List[str]]  # When to load this partition
    memory_usage: int  # Estimated memory usage in KB
    load_time: float  # Estimated load time in ms

class DynamicRuleLoader:
    """Main class for dynamic rule loading and management"""
    
    def __init__(self, rules_directory: str = "knowledge_architecture/systems/dynamic_cursor_rules_system/rule_partitions"):
        self.rules_directory = rules_directory
        self.loaded_partitions: Set[RulePartition] = set()
        self.rule_cache: Dict[RulePartition, str] = {}
        self.rule_metadata: Dict[RulePartition, RuleMetadata] = {}
        self.conflict_resolution_strategy = "priority_based"  # priority_based, user_choice, merge
        
        # Load rule metadata
        self._load_rule_metadata()
        
    def _load_rule_metadata(self):
        """Load metadata for all available rule partitions"""
        self.rule_metadata = {
            RulePartition.BASE_RULES: RuleMetadata(
                name="Base Rules",
                description="Essential operational rules (always loaded)",
                priority=10,
                dependencies=[],
                conflicts=[],
                context_requirements={
                    ContextType.PROJECT_TYPE: ["*"],  # Always required
                    ContextType.TASK_TYPE: ["*"],
                    ContextType.SESSION_STATE: ["*"]
                },
                memory_usage=50,
                load_time=10.0
            ),
            RulePartition.L0_L4_PROTOCOL: RuleMetadata(
                name="L0-L4 Protocol",
                description="L0-L4 documentation protocol rules",
                priority=9,
                dependencies=[RulePartition.BASE_RULES],
                conflicts=[],
                context_requirements={
                    ContextType.PROJECT_TYPE: ["aim_os"],
                    ContextType.PROTOCOL_REQUIRED: ["l0_l4", "documentation"]
                },
                memory_usage=100,
                load_time=25.0
            ),
            RulePartition.AH_PROTOCOL: RuleMetadata(
                name="A-H Protocol",
                description="A-H Protocol workflow rules",
                priority=8,
                dependencies=[RulePartition.BASE_RULES],
                conflicts=[],
                context_requirements={
                    ContextType.PROTOCOL_REQUIRED: ["ah_protocol", "idea_development"],
                    ContextType.TASK_TYPE: ["development", "planning"]
                },
                memory_usage=80,
                load_time=20.0
            ),
            RulePartition.MCP_TOOLS: RuleMetadata(
                name="MCP Tools",
                description="MCP tools integration rules",
                priority=7,
                dependencies=[RulePartition.BASE_RULES],
                conflicts=[],
                context_requirements={
                    ContextType.PROJECT_TYPE: ["aim_os"],
                    ContextType.TASK_TYPE: ["development", "integration"]
                },
                memory_usage=60,
                load_time=15.0
            ),
            RulePartition.QUALITY_STANDARDS: RuleMetadata(
                name="Quality Standards",
                description="Code quality and testing standards",
                priority=6,
                dependencies=[RulePartition.BASE_RULES],
                conflicts=[],
                context_requirements={
                    ContextType.TASK_TYPE: ["development", "testing"],
                    ContextType.COMPLEXITY_LEVEL: ["medium", "high", "critical"]
                },
                memory_usage=40,
                load_time=12.0
            ),
            RulePartition.TESTING_PROTOCOLS: RuleMetadata(
                name="Testing Protocols",
                description="Testing and validation protocols",
                priority=5,
                dependencies=[RulePartition.QUALITY_STANDARDS],
                conflicts=[],
                context_requirements={
                    ContextType.TASK_TYPE: ["testing", "validation"],
                    ContextType.PROJECT_TYPE: ["aim_os"]
                },
                memory_usage=30,
                load_time=8.0
            ),
            RulePartition.DOCUMENTATION_STANDARDS: RuleMetadata(
                name="Documentation Standards",
                description="Documentation and specification standards",
                priority=4,
                dependencies=[RulePartition.BASE_RULES],
                conflicts=[],
                context_requirements={
                    ContextType.TASK_TYPE: ["documentation", "specification"],
                    ContextType.PROTOCOL_REQUIRED: ["documentation"]
                },
                memory_usage=35,
                load_time=10.0
            ),
            RulePartition.PERFORMANCE_OPTIMIZATION: RuleMetadata(
                name="Performance Optimization",
                description="Performance and optimization rules",
                priority=3,
                dependencies=[RulePartition.BASE_RULES],
                conflicts=[],
                context_requirements={
                    ContextType.TASK_TYPE: ["optimization", "performance"],
                    ContextType.COMPLEXITY_LEVEL: ["high", "critical"]
                },
                memory_usage=25,
                load_time=6.0
            ),
            RulePartition.CONSCIOUSNESS_MEMORY: RuleMetadata(
                name="Consciousness & Memory",
                description="Consciousness preservation, memory, and continuity rules (Phase 2 standards)",
                priority=6,
                dependencies=[RulePartition.BASE_RULES],
                conflicts=[],
                context_requirements={
                    ContextType.TASK_TYPE: ["reflection", "memory", "consciousness", "handoff", "question"],
                    ContextType.PROTOCOL_REQUIRED: ["consciousness", "memory", "continuity"]
                },
                memory_usage=120,
                load_time=30.0
            ),
            RulePartition.PLANNING_GOALS: RuleMetadata(
                name="Planning & Goals",
                description="Goal alignment, planning, and strategic coordination rules (Phase 3 standards)",
                priority=7,
                dependencies=[RulePartition.BASE_RULES],
                conflicts=[],
                context_requirements={
                    ContextType.TASK_TYPE: ["planning", "strategy", "goal", "project", "coordination"],
                    ContextType.PROTOCOL_REQUIRED: ["planning", "goals", "strategic"]
                },
                memory_usage=100,
                load_time=25.0
            ),
            RulePartition.SUPPORTING_STANDARDS: RuleMetadata(
                name="Supporting Standards",
                description="Supporting documentation, coordination, navigation, and analysis rules (Phase 4 standards)",
                priority=5,
                dependencies=[RulePartition.BASE_RULES],
                conflicts=[],
                context_requirements={
                    ContextType.TASK_TYPE: ["coordination", "reporting", "navigation", "analysis", "audit"],
                    ContextType.PROTOCOL_REQUIRED: ["supporting", "coordination", "analysis"]
                },
                memory_usage=180,
                load_time=45.0
            ),
            RulePartition.ENHANCED_FOUNDATIONAL: RuleMetadata(
                name="Enhanced Foundational",
                description="Enhanced foundational documentation standards (System Maps, Index, Validation, Templates)",
                priority=8,
                dependencies=[RulePartition.BASE_RULES, RulePartition.DOCUMENTATION_STANDARDS],
                conflicts=[],
                context_requirements={
                    ContextType.TASK_TYPE: ["documentation", "validation", "mapping"],
                    ContextType.PROTOCOL_REQUIRED: ["foundational", "validation", "templates"]
                },
                memory_usage=80,
                load_time=20.0
            )
        }
    
    def analyze_context(self, user_input: str = "", environment_data: Dict = None) -> ContextProfile:
        """Analyze current context to determine which rules to load"""
        if environment_data is None:
            environment_data = {}
            
        # Default context profile
        profile = ContextProfile()
        
        # Analyze user input for context clues
        user_input_lower = user_input.lower()
        
        # Detect project type
        if any(keyword in user_input_lower for keyword in ["aim-os", "aether", "lucid", "mcp"]):
            profile.project_type = "aim_os"
        elif any(keyword in user_input_lower for keyword in ["documentation", "docs", "spec"]):
            profile.project_type = "documentation"
        elif any(keyword in user_input_lower for keyword in ["test", "testing", "validation"]):
            profile.project_type = "testing"
        else:
            profile.project_type = "general"
        
        # Detect task type
        if any(keyword in user_input_lower for keyword in ["implement", "code", "develop", "build", "create"]):
            profile.task_type = "development"
        elif any(keyword in user_input_lower for keyword in ["document", "write", "spec", "l0", "l1", "l2", "l3", "l4"]):
            profile.task_type = "documentation"
        elif any(keyword in user_input_lower for keyword in ["test", "validate", "check", "audit", "verify"]):
            profile.task_type = "testing"
        elif any(keyword in user_input_lower for keyword in ["debug", "fix", "troubleshoot", "error"]):
            profile.task_type = "debugging"
        elif any(keyword in user_input_lower for keyword in ["plan", "design", "architecture", "strategy"]):
            profile.task_type = "planning"
        elif any(keyword in user_input_lower for keyword in ["reflection", "thought", "journal", "consciousness"]):
            profile.task_type = "reflection"
        elif any(keyword in user_input_lower for keyword in ["memory", "context", "active", "handoff"]):
            profile.task_type = "memory"
        elif any(keyword in user_input_lower for keyword in ["goal", "objective", "kpi", "metric", "target"]):
            profile.task_type = "goal"
        elif any(keyword in user_input_lower for keyword in ["coordination", "team", "communication", "status"]):
            profile.task_type = "coordination"
        elif any(keyword in user_input_lower for keyword in ["report", "status", "update", "progress"]):
            profile.task_type = "reporting"
        elif any(keyword in user_input_lower for keyword in ["navigation", "index", "map", "concept"]):
            profile.task_type = "navigation"
        elif any(keyword in user_input_lower for keyword in ["analysis", "audit", "research", "evaluation"]):
            profile.task_type = "analysis"
        elif any(keyword in user_input_lower for keyword in ["map", "system_map", "atlas", "relationship"]):
            profile.task_type = "mapping"
        
        # Detect required protocols
        profile.protocol_required = []
        if any(keyword in user_input_lower for keyword in ["l0", "l1", "l2", "l3", "l4", "documentation"]):
            profile.protocol_required.append("l0_l4")
        if any(keyword in user_input_lower for keyword in ["a-h", "ah protocol", "idea development"]):
            profile.protocol_required.append("ah_protocol")
        if any(keyword in user_input_lower for keyword in ["lucid", "consciousness", "mcp"]):
            profile.protocol_required.append("lucid")
        if any(keyword in user_input_lower for keyword in ["mcp", "tools", "integration"]):
            profile.protocol_required.append("mcp_tools")
        # Phase 2: Consciousness & Memory
        if any(keyword in user_input_lower for keyword in ["consciousness", "memory", "thought", "journal", "decision", "learning", "session", "continuity"]):
            profile.protocol_required.append("consciousness")
        if any(keyword in user_input_lower for keyword in ["memory", "context", "active", "handoff", "continuity"]):
            profile.protocol_required.append("memory")
        # Phase 3: Planning & Goals
        if any(keyword in user_input_lower for keyword in ["planning", "goal", "objective", "key result", "kpi", "metric", "task", "dependency"]):
            profile.protocol_required.append("planning")
        if any(keyword in user_input_lower for keyword in ["goal", "objective", "kpi", "metric", "task", "project", "hierarchy"]):
            profile.protocol_required.append("goals")
        if any(keyword in user_input_lower for keyword in ["strategic", "planning", "goal", "objective"]):
            profile.protocol_required.append("strategic")
        # Phase 4: Supporting Standards
        if any(keyword in user_input_lower for keyword in ["supporting", "timeline", "coordination", "status", "report", "navigation", "index"]):
            profile.protocol_required.append("supporting")
        if any(keyword in user_input_lower for keyword in ["coordination", "communication", "team", "status", "report"]):
            profile.protocol_required.append("coordination")
        if any(keyword in user_input_lower for keyword in ["analysis", "audit", "research", "evaluation", "assessment"]):
            profile.protocol_required.append("analysis")
        # Enhanced Foundational
        if any(keyword in user_input_lower for keyword in ["foundational", "system_map", "system_index", "validation", "template"]):
            profile.protocol_required.append("foundational")
        if any(keyword in user_input_lower for keyword in ["validation", "gate", "check", "quality", "compliance"]):
            profile.protocol_required.append("validation")
        if any(keyword in user_input_lower for keyword in ["template", "library", "standard", "documentation"]):
            profile.protocol_required.append("templates")
        
        # Detect complexity level
        if any(keyword in user_input_lower for keyword in ["critical", "urgent", "emergency", "tier 3"]):
            profile.complexity_level = "critical"
        elif any(keyword in user_input_lower for keyword in ["complex", "major", "tier 2", "architecture"]):
            profile.complexity_level = "high"
        elif any(keyword in user_input_lower for keyword in ["simple", "minor", "tier 1", "fix"]):
            profile.complexity_level = "low"
        else:
            profile.complexity_level = "medium"
        
        # Detect confidence level (simplified heuristic)
        if any(keyword in user_input_lower for keyword in ["confident", "sure", "definitely"]):
            profile.confidence_level = 0.9
        elif any(keyword in user_input_lower for keyword in ["uncertain", "unsure", "maybe"]):
            profile.confidence_level = 0.5
        else:
            profile.confidence_level = 0.8
        
        return profile
    
    def select_rules(self, context_profile: ContextProfile) -> List[RulePartition]:
        """Select which rule partitions to load based on context"""
        selected_partitions = []
        
        # Always include base rules
        selected_partitions.append(RulePartition.BASE_RULES)
        
        # Select additional partitions based on context
        for partition, metadata in self.rule_metadata.items():
            if partition == RulePartition.BASE_RULES:
                continue  # Already included
                
            should_load = False
            
            # Check context requirements
            for context_type, required_values in metadata.context_requirements.items():
                if context_type == ContextType.PROJECT_TYPE:
                    if "*" in required_values or context_profile.project_type in required_values:
                        should_load = True
                elif context_type == ContextType.TASK_TYPE:
                    if "*" in required_values or context_profile.task_type in required_values:
                        should_load = True
                elif context_type == ContextType.PROTOCOL_REQUIRED:
                    if any(protocol in context_profile.protocol_required for protocol in required_values):
                        should_load = True
                elif context_type == ContextType.COMPLEXITY_LEVEL:
                    if context_profile.complexity_level in required_values:
                        should_load = True
            
            if should_load:
                selected_partitions.append(partition)
        
        # Sort by priority (higher priority first)
        selected_partitions.sort(key=lambda p: self.rule_metadata[p].priority, reverse=True)
        
        return selected_partitions
    
    def load_rule_partition(self, partition: RulePartition) -> str:
        """Load a specific rule partition from file"""
        if partition in self.rule_cache:
            return self.rule_cache[partition]
        
        # Map partition to filename
        partition_files = {
            RulePartition.BASE_RULES: "base_rules.cursorrules",
            RulePartition.L0_L4_PROTOCOL: "l0_l4_protocol.cursorrules",
            RulePartition.AH_PROTOCOL: "ah_protocol.cursorrules",
            RulePartition.MCP_TOOLS: "mcp_tools.cursorrules",
            RulePartition.QUALITY_STANDARDS: "quality_standards.cursorrules",
            RulePartition.TESTING_PROTOCOLS: "testing_protocols.cursorrules",
            RulePartition.DOCUMENTATION_STANDARDS: "documentation_standards.cursorrules",
            RulePartition.PERFORMANCE_OPTIMIZATION: "performance_optimization.cursorrules",
            RulePartition.CONSCIOUSNESS_MEMORY: "consciousness_memory.cursorrules",
            RulePartition.PLANNING_GOALS: "planning_goals.cursorrules",
            RulePartition.SUPPORTING_STANDARDS: "supporting_standards.cursorrules",
            RulePartition.ENHANCED_FOUNDATIONAL: "enhanced_foundational.cursorrules"
        }
        
        filename = partition_files.get(partition)
        if not filename:
            raise ValueError(f"No filename mapping for partition {partition}")
        
        filepath = os.path.join(self.rules_directory, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Cache the content
            self.rule_cache[partition] = content
            return content
            
        except FileNotFoundError:
            print(f"Warning: Rule partition file not found: {filepath}")
            return f"# {partition.value} - File not found\n# This partition is not available.\n"
        except Exception as e:
            print(f"Error loading rule partition {partition}: {e}")
            return f"# {partition.value} - Error loading\n# Error: {e}\n"
    
    def resolve_conflicts(self, partitions: List[RulePartition]) -> List[RulePartition]:
        """Resolve conflicts between rule partitions"""
        if self.conflict_resolution_strategy == "priority_based":
            # Keep higher priority partitions, remove conflicting lower priority ones
            resolved = []
            for partition in partitions:
                conflicts = self.rule_metadata[partition].conflicts
                has_conflict = any(conflict in resolved for conflict in conflicts)
                
                if not has_conflict:
                    resolved.append(partition)
                else:
                    print(f"Warning: Skipping {partition.value} due to conflict with loaded partitions")
            
            return resolved
        
        # Add other conflict resolution strategies here
        return partitions
    
    def generate_cursor_rules(self, context_profile: ContextProfile) -> str:
        """Generate the final .cursorrules content based on context"""
        start_time = time.perf_counter()
        
        # Select rule partitions
        selected_partitions = self.select_rules(context_profile)
        
        # Resolve conflicts
        resolved_partitions = self.resolve_conflicts(selected_partitions)
        
        # Load and combine rules
        combined_rules = []
        combined_rules.append("# Dynamic Cursor Rules - Auto-generated")
        combined_rules.append(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        combined_rules.append(f"# Context: {context_profile.project_type}/{context_profile.task_type}")
        combined_rules.append(f"# Protocols: {', '.join(context_profile.protocol_required) if context_profile.protocol_required else 'None'}")
        combined_rules.append(f"# Complexity: {context_profile.complexity_level}")
        combined_rules.append("")
        
        # Load each partition
        for partition in resolved_partitions:
            partition_content = self.load_rule_partition(partition)
            combined_rules.append(f"# === {self.rule_metadata[partition].name} ===")
            combined_rules.append(partition_content)
            combined_rules.append("")
        
        # Add footer
        combined_rules.append("# === End of Dynamic Rules ===")
        combined_rules.append(f"# Loaded {len(resolved_partitions)} partitions in {time.perf_counter() - start_time:.2f}ms")
        
        # Update loaded partitions
        self.loaded_partitions = set(resolved_partitions)
        
        return "\n".join(combined_rules)
    
    def save_cursor_rules(self, content: str, output_path: str = ".cursorrules"):
        """Save the generated rules to .cursorrules file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Dynamic rules saved to {output_path}")
        except Exception as e:
            print(f"Error saving rules to {output_path}: {e}")
    
    def get_loaded_partitions(self) -> List[str]:
        """Get list of currently loaded partitions"""
        return [partition.value for partition in self.loaded_partitions]
    
    def get_memory_usage(self) -> int:
        """Get estimated memory usage of loaded partitions"""
        total_memory = 0
        for partition in self.loaded_partitions:
            total_memory += self.rule_metadata[partition].memory_usage
        return total_memory

def main():
    """Main function for testing the dynamic rule loader"""
    loader = DynamicRuleLoader()
    
    # Test different contexts
    test_contexts = [
        ("I need to implement a new feature for AIM-OS", {}),
        ("Let's document the L0-L4 protocol for the new system", {}),
        ("I want to test the MCP tools integration", {}),
        ("Help me debug this performance issue", {}),
        ("Plan out the next phase of development", {})
    ]
    
    for user_input, env_data in test_contexts:
        print(f"\n--- Testing: '{user_input}' ---")
        
        # Analyze context
        context = loader.analyze_context(user_input, env_data)
        print(f"Context: {context.project_type}/{context.task_type}, Protocols: {context.protocol_required}")
        
        # Generate rules
        rules_content = loader.generate_cursor_rules(context)
        
        # Show loaded partitions
        loaded = loader.get_loaded_partitions()
        print(f"Loaded partitions: {loaded}")
        print(f"Memory usage: {loader.get_memory_usage()}KB")
        
        # Save to test file
        test_filename = f"test_rules_{context.project_type}_{context.task_type}.cursorrules"
        loader.save_cursor_rules(rules_content, test_filename)

if __name__ == "__main__":
    main()
