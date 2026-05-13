# L3 Detailed Implementation: Dynamic Cursor Rules System

## Implementation Guide

This document provides comprehensive implementation details for the Dynamic Cursor Rules System, including code examples, configuration details, and step-by-step implementation instructions.

## Core Implementation Details

### 1. Dynamic Rule Loader Implementation

#### Core Class Structure
```python
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import time
import json
import os

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
    CONSCIOUSNESS_MEMORY = "consciousness_memory"  # Phase 2: 6 standards
    PLANNING_GOALS = "planning_goals"  # Phase 3: 5 standards
    SUPPORTING_STANDARDS = "supporting_standards"  # Phase 4: 17 standards
    ENHANCED_FOUNDATIONAL = "enhanced_foundational"  # Phase 1: 4 enhancements

@dataclass
class ContextProfile:
    """Profile of current context for rule selection"""
    project_type: str = "aim_os"
    task_type: str = "development"
    protocol_required: List[str] = None
    session_state: str = "active"
    user_preference: str = "standard"
    confidence_level: float = 0.8
    complexity_level: str = "medium"
    detected_intents: List[str] = None
    relevant_keywords: List[str] = None
    suggested_categories: List[str] = None
    
    def __post_init__(self):
        if self.protocol_required is None:
            self.protocol_required = []
        if self.detected_intents is None:
            self.detected_intents = []
        if self.relevant_keywords is None:
            self.relevant_keywords = []
        if self.suggested_categories is None:
            self.suggested_categories = []
```

#### Dynamic Rule Loader Core
```python
class DynamicRuleLoader:
    """Main class for dynamic rule loading and management"""
    
    def __init__(self, rules_directory: str = "knowledge_architecture/systems/dynamic_cursor_rules_system/rule_partitions"):
        self.rules_directory = rules_directory
        self.loaded_partitions: Set[RulePartition] = set()
        self.rule_cache: Dict[RulePartition, str] = {}
        self.rule_metadata: Dict[RulePartition, RuleMetadata] = {}
        self.conflict_resolution_strategy = "priority_based"
        
        # Load rule metadata
        self._load_rule_metadata()
    
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
        if any(keyword in user_input_lower for keyword in ["implement", "code", "develop", "build"]):
            profile.task_type = "development"
        elif any(keyword in user_input_lower for keyword in ["document", "write", "spec", "l0", "l1", "l2", "l3", "l4"]):
            profile.task_type = "documentation"
        elif any(keyword in user_input_lower for keyword in ["test", "validate", "check", "audit"]):
            profile.task_type = "testing"
        elif any(keyword in user_input_lower for keyword in ["debug", "fix", "troubleshoot"]):
            profile.task_type = "debugging"
        elif any(keyword in user_input_lower for keyword in ["plan", "design", "architecture"]):
            profile.task_type = "planning"
        
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
        
        # Detect complexity level
        if any(keyword in user_input_lower for keyword in ["critical", "urgent", "emergency", "tier 3"]):
            profile.complexity_level = "critical"
        elif any(keyword in user_input_lower for keyword in ["complex", "major", "tier 2", "architecture"]):
            profile.complexity_level = "high"
        elif any(keyword in user_input_lower for keyword in ["simple", "minor", "tier 1", "fix"]):
            profile.complexity_level = "low"
        else:
            profile.complexity_level = "medium"
        
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
```

### 2. Rule Partition Management

#### Rule Metadata Structure
```python
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

class RulePartitionManager:
    """Manages rule partitions and their metadata"""
    
    def __init__(self):
        self.partitions: Dict[RulePartition, RuleMetadata] = {}
        self.dependency_graph: Dict[RulePartition, List[RulePartition]] = {}
        self.conflict_matrix: Dict[RulePartition, List[RulePartition]] = {}
    
    def register_partition(self, partition: RulePartition, metadata: RuleMetadata):
        """Register a rule partition with metadata"""
        self.partitions[partition] = metadata
        self._update_dependency_graph(partition, metadata)
        self._update_conflict_matrix(partition, metadata)
    
    def get_partition_metadata(self, partition: RulePartition) -> RuleMetadata:
        """Get metadata for a partition"""
        return self.partitions.get(partition)
    
    def get_dependencies(self, partition: RulePartition) -> List[RulePartition]:
        """Get dependencies for a partition"""
        return self.dependency_graph.get(partition, [])
    
    def get_conflicts(self, partition: RulePartition) -> List[RulePartition]:
        """Get conflicts for a partition"""
        return self.conflict_matrix.get(partition, [])
    
    def _update_dependency_graph(self, partition: RulePartition, metadata: RuleMetadata):
        """Update dependency graph"""
        self.dependency_graph[partition] = []
        for dep_name in metadata.dependencies:
            for p, m in self.partitions.items():
                if m.name == dep_name:
                    self.dependency_graph[partition].append(p)
                    break
    
    def _update_conflict_matrix(self, partition: RulePartition, metadata: RuleMetadata):
        """Update conflict matrix"""
        self.conflict_matrix[partition] = []
        for conflict_name in metadata.conflicts:
            for p, m in self.partitions.items():
                if m.name == conflict_name:
                    self.conflict_matrix[partition].append(p)
                    break
```

### 3. Context Analysis Engine

#### Advanced Context Analysis
```python
class AdvancedContextAnalyzer:
    """Advanced context analysis with machine learning capabilities"""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.keywords_config = self._load_keywords_config()
        self.intent_patterns = self._load_intent_patterns()
        self.complexity_indicators = self._load_complexity_indicators()
        self.urgency_indicators = self._load_urgency_indicators()
        self.ml_model = self._load_ml_model() if model_path else None
    
    def analyze_input(self, user_input: str, environment_data: Dict[str, Any] = None) -> ContextProfile:
        """Advanced context analysis with ML enhancement"""
        # Initialize profile
        profile = ContextProfile()
        profile.raw_input = user_input
        profile.environment = environment_data or {}
        
        # Basic analysis
        self._analyze_text(user_input, profile)
        self._analyze_environment(environment_data, profile)
        self._detect_intents(profile)
        self._assess_urgency(profile)
        self._assess_complexity(profile)
        self._assess_tier_implication(profile)
        
        # ML enhancement if available
        if self.ml_model:
            profile = self._ml_enhance_profile(profile)
        
        return profile
    
    def _analyze_text(self, text: str, profile: ContextProfile):
        """Analyze text for keywords and patterns"""
        text_lower = text.lower()
        
        # Extract keywords
        for category, keywords in self.keywords_config.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    if category not in profile.suggested_categories:
                        profile.suggested_categories.append(category)
                    if keyword not in profile.relevant_keywords:
                        profile.relevant_keywords.append(keyword)
    
    def _detect_intents(self, profile: ContextProfile):
        """Detect user intents from input"""
        text_lower = profile.raw_input.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    profile.detected_intents.append(intent)
                    break
    
    def _assess_urgency(self, profile: ContextProfile):
        """Assess urgency level"""
        text_lower = profile.raw_input.lower()
        
        if any(indicator in text_lower for indicator in self.urgency_indicators['high']):
            profile.urgency = "high"
        elif any(indicator in text_lower for indicator in self.urgency_indicators['medium']):
            profile.urgency = "medium"
        else:
            profile.urgency = "low"
    
    def _assess_complexity(self, profile: ContextProfile):
        """Assess task complexity"""
        text_lower = profile.raw_input.lower()
        word_count = len(profile.raw_input.split())
        unique_words = len(set(text_lower.split()))
        
        # Check complexity indicators
        if any(indicator in text_lower for indicator in self.complexity_indicators['high']):
            profile.complexity_level = "high"
        elif any(indicator in text_lower for indicator in self.complexity_indicators['low']):
            profile.complexity_level = "low"
        else:
            # Heuristic based on text characteristics
            if word_count > 100 or unique_words > 50:
                profile.complexity_level = "high"
            elif word_count > 30 or unique_words > 20:
                profile.complexity_level = "medium"
            else:
                profile.complexity_level = "low"
    
    def _ml_enhance_profile(self, profile: ContextProfile) -> ContextProfile:
        """Enhance profile using machine learning"""
        if not self.ml_model:
            return profile
        
        # Prepare features for ML model
        features = self._extract_ml_features(profile)
        
        # Get ML predictions
        predictions = self.ml_model.predict(features)
        
        # Update profile with ML insights
        profile.confidence_level = predictions.get('confidence', profile.confidence_level)
        profile.complexity_level = predictions.get('complexity', profile.complexity_level)
        
        return profile
```

### 4. Rule Composition Engine

#### Intelligent Rule Composition
```python
class RuleCompositionEngine:
    """Intelligent rule composition and conflict resolution"""
    
    def __init__(self, conflict_resolution_strategy: str = "priority_based"):
        self.conflict_resolution_strategy = conflict_resolution_strategy
        self.composition_rules = self._load_composition_rules()
        self.conflict_resolvers = self._load_conflict_resolvers()
    
    def compose_rules(self, partitions: List[RulePartition], context: ContextProfile) -> str:
        """Compose rules from multiple partitions"""
        # Resolve conflicts
        resolved_partitions = self.resolve_conflicts(partitions)
        
        # Compose rules
        composed_rules = self._compose_rule_content(resolved_partitions, context)
        
        # Apply composition rules
        final_rules = self._apply_composition_rules(composed_rules, context)
        
        return final_rules
    
    def resolve_conflicts(self, partitions: List[RulePartition]) -> List[RulePartition]:
        """Resolve conflicts between partitions"""
        if self.conflict_resolution_strategy == "priority_based":
            return self._resolve_conflicts_priority_based(partitions)
        elif self.conflict_resolution_strategy == "user_choice":
            return self._resolve_conflicts_user_choice(partitions)
        else:
            return partitions
    
    def _resolve_conflicts_priority_based(self, partitions: List[RulePartition]) -> List[RulePartition]:
        """Resolve conflicts using priority-based strategy"""
        resolved = []
        partition_priorities = {p: self._get_partition_priority(p) for p in partitions}
        
        # Sort by priority (higher first)
        sorted_partitions = sorted(partitions, key=lambda p: partition_priorities[p], reverse=True)
        
        for partition in sorted_partitions:
            conflicts = self._get_partition_conflicts(partition)
            has_conflict = any(conflict in resolved for conflict in conflicts)
            
            if not has_conflict:
                resolved.append(partition)
            else:
                print(f"Warning: Skipping {partition.value} due to conflict with loaded partitions")
        
        return resolved
    
    def _compose_rule_content(self, partitions: List[RulePartition], context: ContextProfile) -> str:
        """Compose rule content from partitions"""
        composed_parts = []
        
        # Add header
        composed_parts.append(self._generate_header(context))
        
        # Add each partition
        for partition in partitions:
            partition_content = self._load_partition_content(partition)
            composed_parts.append(f"# === {partition.value.upper()} ===")
            composed_parts.append(partition_content)
            composed_parts.append("")
        
        # Add footer
        composed_parts.append(self._generate_footer(len(partitions)))
        
        return "\n".join(composed_parts)
```

### 5. Performance Optimization

#### Caching System
```python
class RuleCache:
    """Intelligent caching system for rules and context"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_times: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[str]:
        """Get cached rule content"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check TTL
        if time.time() - entry.timestamp > self.ttl:
            self.remove(key)
            return None
        
        # Update access time
        self.access_times[key] = time.time()
        
        return entry.content
    
    def put(self, key: str, content: str):
        """Cache rule content"""
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = CacheEntry(content, time.time())
        self.access_times[key] = time.time()
    
    def _evict_oldest(self):
        """Evict oldest cache entry"""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self.remove(oldest_key)
    
    def remove(self, key: str):
        """Remove cache entry"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_times:
            del self.access_times[key]

@dataclass
class CacheEntry:
    content: str
    timestamp: float
```

#### Memory Management
```python
class MemoryManager:
    """Memory management for rule system"""
    
    def __init__(self, max_memory_mb: int = 500):
        self.max_memory_mb = max_memory_mb
        self.current_memory_mb = 0
        self.memory_usage: Dict[str, int] = {}
    
    def allocate_memory(self, component: str, size_bytes: int) -> bool:
        """Allocate memory for component"""
        size_mb = size_bytes / (1024 * 1024)
        
        if self.current_memory_mb + size_mb > self.max_memory_mb:
            return False
        
        self.current_memory_mb += size_mb
        self.memory_usage[component] = size_bytes
        return True
    
    def deallocate_memory(self, component: str):
        """Deallocate memory for component"""
        if component in self.memory_usage:
            size_mb = self.memory_usage[component] / (1024 * 1024)
            self.current_memory_mb -= size_mb
            del self.memory_usage[component]
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage"""
        return {
            "current_mb": self.current_memory_mb,
            "max_mb": self.max_memory_mb,
            "usage_percent": (self.current_memory_mb / self.max_memory_mb) * 100,
            "components": self.memory_usage.copy()
        }
```

### 6. Integration System

#### Cursor IDE Integration
```python
class CursorIDEIntegration:
    """Integration with Cursor IDE"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.cursor_rules_path = self.project_root / ".cursorrules"
        self.backup_path = self.project_root / ".cursorrules.backup"
    
    def install_dynamic_rules(self, rules_content: str, backup_existing: bool = True) -> bool:
        """Install dynamic rules to Cursor IDE"""
        try:
            # Backup existing rules
            if backup_existing and self.cursor_rules_path.exists():
                self._backup_existing_rules()
            
            # Write new rules
            with open(self.cursor_rules_path, 'w', encoding='utf-8') as f:
                f.write(rules_content)
            
            return True
            
        except Exception as e:
            print(f"Error installing dynamic rules: {e}")
            return False
    
    def _backup_existing_rules(self):
        """Backup existing .cursorrules file"""
        if self.cursor_rules_path.exists():
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_path.with_suffix(f".{timestamp}.backup")
            self.cursor_rules_path.rename(backup_file)
            print(f"Backed up existing rules to {backup_file}")
    
    def restore_backup(self, backup_file: str = None) -> bool:
        """Restore from backup"""
        try:
            if backup_file is None:
                # Find latest backup
                backup_files = list(self.project_root.glob(".cursorrules.*.backup"))
                if not backup_files:
                    return False
                backup_file = max(backup_files, key=os.path.getctime)
            
            # Restore from backup
            shutil.copy2(backup_file, self.cursor_rules_path)
            print(f"Restored rules from {backup_file}")
            return True
            
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
```

### 7. Configuration Management

#### Configuration System
```python
class ConfigurationManager:
    """Manages system configuration"""
    
    def __init__(self, config_path: str = "rule_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "version": "1.0",
            "description": "Dynamic Cursor Rules System Configuration",
            "rule_partitions": {
                "base_rules": {
                    "filename": "base_rules.cursorrules",
                    "priority": 10,
                    "always_load": True,
                    "dependencies": [],
                    "conflicts": [],
                    "context_requirements": {
                        "project_type": ["*"],
                        "task_type": ["*"],
                        "session_state": ["*"]
                    },
                    "memory_usage_kb": 50,
                    "load_time_ms": 10.0
                }
            },
            "performance": {
                "max_memory_usage": 0.8,
                "max_cpu_usage": 0.8,
                "response_time_threshold": 1000,
                "alert_enabled": True
            },
            "conflict_resolution": {
                "strategy": "priority_based",
                "fallback_strategy": "user_choice",
                "merge_conflicts": False
            }
        }
    
    def get_config(self, key: str = None) -> Any:
        """Get configuration value"""
        if key is None:
            return self.config
        
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k)
            if value is None:
                break
        return value
    
    def update_config(self, key: str, value: Any):
        """Update configuration value"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        
        # Save to file
        self._save_config()
    
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
```

## Testing Implementation

### 1. Unit Tests
```python
import pytest
from dynamic_rule_loader import DynamicRuleLoader, ContextProfile
from rule_partition_manager import RulePartitionManager

class TestDynamicRuleLoader:
    def test_initialization(self):
        """Test system initialization"""
        loader = DynamicRuleLoader()
        assert loader.rules_directory is not None
        assert loader.rule_cache is not None
        assert loader.rule_metadata is not None
    
    def test_context_analysis(self):
        """Test context analysis"""
        loader = DynamicRuleLoader()
        context = loader.analyze_context("I need to implement L0-L4 documentation")
        
        assert context.project_type == "aim_os"
        assert "l0_l4" in context.protocol_required
        assert context.task_type == "documentation"
    
    def test_rule_selection(self):
        """Test rule selection"""
        loader = DynamicRuleLoader()
        context = ContextProfile(
            project_type="aim_os",
            task_type="development",
            protocol_required=["l0_l4", "mcp_tools"]
        )
        
        selected = loader.select_rules(context)
        assert RulePartition.BASE_RULES in selected
        assert RulePartition.L0_L4_PROTOCOL in selected
        assert RulePartition.MCP_TOOLS in selected
    
    def test_rule_generation(self):
        """Test rule generation"""
        loader = DynamicRuleLoader()
        context = ContextProfile(project_type="aim_os", task_type="development")
        
        rules = loader.generate_cursor_rules(context)
        assert "# Dynamic Cursor Rules - Auto-generated" in rules
        assert "aim_os" in rules
        assert "development" in rules
```

### 2. Integration Tests
```python
class TestIntegration:
    def test_end_to_end_workflow(self):
        """Test complete workflow"""
        loader = DynamicRuleLoader()
        
        # Test context analysis
        context = loader.analyze_context(
            "I need to implement L0-L4 documentation for the new system",
            {"active_project": "AIM-OS", "open_files": ["new_system.py"]}
        )
        
        # Test rule selection
        selected = loader.select_rules(context)
        assert len(selected) > 0
        
        # Test rule generation
        rules = loader.generate_cursor_rules(context)
        assert len(rules) > 0
        assert "L0-L4" in rules
    
    def test_performance_requirements(self):
        """Test performance requirements"""
        loader = DynamicRuleLoader()
        
        start_time = time.perf_counter()
        rules = loader.generate_cursor_rules(ContextProfile())
        end_time = time.perf_counter()
        
        duration_ms = (end_time - start_time) * 1000
        assert duration_ms < 100  # Should be under 100ms
```

### 3. Performance Tests
```python
class TestPerformance:
    def test_memory_usage(self):
        """Test memory usage"""
        loader = DynamicRuleLoader()
        
        # Generate rules multiple times
        for i in range(100):
            context = ContextProfile(project_type="aim_os", task_type="development")
            rules = loader.generate_cursor_rules(context)
        
        # Check memory usage
        memory_usage = loader.get_memory_usage()
        assert memory_usage < 500  # Should be under 500KB
    
    def test_load_time(self):
        """Test load time"""
        loader = DynamicRuleLoader()
        
        times = []
        for i in range(10):
            start_time = time.perf_counter()
            context = ContextProfile(project_type="aim_os", task_type="development")
            rules = loader.generate_cursor_rules(context)
            end_time = time.perf_counter()
            
            duration_ms = (end_time - start_time) * 1000
            times.append(duration_ms)
        
        avg_time = sum(times) / len(times)
        assert avg_time < 100  # Average should be under 100ms
```

## Deployment Guide

### 1. Installation
```bash
# Clone repository
git clone <repository_url>
cd dynamic_cursor_rules_system

# Install dependencies
pip install -r requirements.txt

# Configure system
cp config/rule_config.json.example config/rule_config.json
# Edit configuration as needed

# Initialize data directories
mkdir -p data/cache
mkdir -p logs
```

### 2. Running the System
```bash
# Install dynamic rules
python integrate_dynamic_rules.py

# Or run with specific configuration
python integrate_dynamic_rules.py --config config/rule_config.json

# Check status
python manage_dynamic_rules.py status

# Update rules for context
python manage_dynamic_rules.py update "I need to implement L0-L4 documentation"
```

### 3. Monitoring
```bash
# Check system status
python manage_dynamic_rules.py status

# View performance metrics
python -m monitoring.performance_dashboard

# Check logs
tail -f logs/dynamic_rules_system.log
```

## Maintenance and Operations

### 1. Regular Maintenance
- Monitor performance metrics
- Update rule partitions
- Clean up old cache files
- Backup configuration and data

### 2. Troubleshooting
- Check rule partition files
- Verify context analysis
- Review error logs
- Test rule generation

### 3. Scaling
- Add more rule partitions
- Increase memory limits
- Optimize context analysis
- Improve caching strategies

---
*This implementation guide provides comprehensive details for building and operating the Dynamic Cursor Rules System.*
