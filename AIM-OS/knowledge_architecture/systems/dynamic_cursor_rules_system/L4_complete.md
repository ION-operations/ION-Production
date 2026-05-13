# L4 Complete Reference: Dynamic Cursor Rules System

## Complete System Reference

This document provides the complete reference for the Dynamic Cursor Rules System, including all implementation details, API references, configuration options, troubleshooting guides, and operational procedures.

## System Overview

The Dynamic Cursor Rules System is a production-ready, context-aware rule management framework that revolutionizes how Cursor IDE rules are managed and applied. The system intelligently partitions, loads, and applies rules based on real-time context analysis, ensuring optimal performance while maintaining comprehensive protocol compliance.

## Complete API Reference

### 1. DynamicRuleLoader Class

#### Constructor
```python
DynamicRuleLoader(rules_directory: str = "knowledge_architecture/systems/dynamic_cursor_rules_system/rule_partitions")
```

**Parameters:**
- `rules_directory` (str): Path to rule partitions directory

**Returns:** DynamicRuleLoader instance

#### Methods

##### analyze_context(user_input: str = "", environment_data: Dict = None) -> ContextProfile
Analyze current context to determine which rules to load.

**Parameters:**
- `user_input` (str): User's input text
- `environment_data` (Dict): Environmental context data

**Returns:** ContextProfile object

**Example:**
```python
loader = DynamicRuleLoader()
context = loader.analyze_context(
    "I need to implement L0-L4 documentation",
    {"active_project": "AIM-OS", "open_files": ["new_system.py"]}
)
print(f"Project type: {context.project_type}")
print(f"Required protocols: {context.protocol_required}")
```

##### select_rules(context_profile: ContextProfile) -> List[RulePartition]
Select which rule partitions to load based on context.

**Parameters:**
- `context_profile` (ContextProfile): Analyzed context profile

**Returns:** List of selected rule partitions

**Example:**
```python
selected = loader.select_rules(context)
print(f"Selected {len(selected)} rule partitions")
```

##### generate_cursor_rules(context_profile: ContextProfile) -> str
Generate the final .cursorrules content based on context.

**Parameters:**
- `context_profile` (ContextProfile): Context profile for rule generation

**Returns:** Generated .cursorrules content

**Example:**
```python
rules_content = loader.generate_cursor_rules(context)
with open('.cursorrules', 'w') as f:
    f.write(rules_content)
```

### 2. ContextProfile Class

#### Constructor
```python
ContextProfile(
    project_type: str = "aim_os",
    task_type: str = "development",
    protocol_required: List[str] = None,
    session_state: str = "active",
    user_preference: str = "standard",
    confidence_level: float = 0.8,
    complexity_level: str = "medium",
    detected_intents: List[str] = None,
    relevant_keywords: List[str] = None,
    suggested_categories: List[str] = None
)
```

#### Properties
- `project_type` (str): Type of project (aim_os, documentation, testing, general)
- `task_type` (str): Type of task (development, documentation, testing, debugging, planning)
- `protocol_required` (List[str]): Required protocols (l0_l4, ah_protocol, lucid, mcp_tools)
- `session_state` (str): Current session state (active, idle, paused)
- `user_preference` (str): User preference level (standard, comprehensive, minimal)
- `confidence_level` (float): Confidence in context analysis (0.0-1.0)
- `complexity_level` (str): Task complexity (low, medium, high, critical)
- `detected_intents` (List[str]): Detected user intents
- `relevant_keywords` (List[str]): Relevant keywords from input
- `suggested_categories` (List[str]): Suggested rule categories

### 3. RulePartitionManager Class

#### Constructor
```python
RulePartitionManager()
```

#### Methods

##### register_partition(partition: RulePartition, metadata: RuleMetadata)
Register a rule partition with metadata.

**Parameters:**
- `partition` (RulePartition): Rule partition enum
- `metadata` (RuleMetadata): Partition metadata

**Example:**
```python
manager = RulePartitionManager()
metadata = RuleMetadata(
    name="L0-L4 Protocol",
    description="L0-L4 documentation protocol rules",
    priority=8,
    dependencies=[],
    conflicts=[],
    context_requirements={
        ContextType.PROTOCOL_REQUIRED: ["l0_l4"],
        ContextType.TASK_TYPE: ["documentation"]
    },
    memory_usage=75,
    load_time=15.0
)
manager.register_partition(RulePartition.L0_L4_PROTOCOL, metadata)
```

##### get_partition_metadata(partition: RulePartition) -> RuleMetadata
Get metadata for a partition.

**Parameters:**
- `partition` (RulePartition): Rule partition enum

**Returns:** RuleMetadata object

##### get_dependencies(partition: RulePartition) -> List[RulePartition]
Get dependencies for a partition.

**Parameters:**
- `partition` (RulePartition): Rule partition enum

**Returns:** List of dependent partitions

##### get_conflicts(partition: RulePartition) -> List[RulePartition]
Get conflicts for a partition.

**Parameters:**
- `partition` (RulePartition): Rule partition enum

**Returns:** List of conflicting partitions

### 4. AdvancedContextAnalyzer Class

#### Constructor
```python
AdvancedContextAnalyzer(model_path: str = None)
```

**Parameters:**
- `model_path` (str): Path to ML model for enhancement (optional)

#### Methods

##### analyze_input(user_input: str, environment_data: Dict[str, Any] = None) -> ContextProfile
Advanced context analysis with ML enhancement.

**Parameters:**
- `user_input` (str): User input text
- `environment_data` (Dict[str, Any]): Environmental data

**Returns:** Enhanced ContextProfile object

**Example:**
```python
analyzer = AdvancedContextAnalyzer("models/context_model.pkl")
context = analyzer.analyze_input(
    "I need to implement L0-L4 documentation for the new system",
    {"active_project": "AIM-OS", "open_files": ["new_system.py"]}
)
print(f"Detected intents: {context.detected_intents}")
print(f"Confidence: {context.confidence_level}")
```

### 5. RuleCompositionEngine Class

#### Constructor
```python
RuleCompositionEngine(conflict_resolution_strategy: str = "priority_based")
```

**Parameters:**
- `conflict_resolution_strategy` (str): Strategy for resolving conflicts (priority_based, user_choice)

#### Methods

##### compose_rules(partitions: List[RulePartition], context: ContextProfile) -> str
Compose rules from multiple partitions.

**Parameters:**
- `partitions` (List[RulePartition]): List of rule partitions
- `context` (ContextProfile): Context profile

**Returns:** Composed rule content

**Example:**
```python
engine = RuleCompositionEngine()
partitions = [RulePartition.BASE_RULES, RulePartition.L0_L4_PROTOCOL]
composed_rules = engine.compose_rules(partitions, context)
```

##### resolve_conflicts(partitions: List[RulePartition]) -> List[RulePartition]
Resolve conflicts between partitions.

**Parameters:**
- `partitions` (List[RulePartition]): List of rule partitions

**Returns:** List of resolved partitions

### 6. RuleCache Class

#### Constructor
```python
RuleCache(max_size: int = 1000, ttl: int = 3600)
```

**Parameters:**
- `max_size` (int): Maximum cache size
- `ttl` (int): Time-to-live in seconds

#### Methods

##### get(key: str) -> Optional[str]
Get cached rule content.

**Parameters:**
- `key` (str): Cache key

**Returns:** Cached content or None

##### put(key: str, content: str)
Cache rule content.

**Parameters:**
- `key` (str): Cache key
- `content` (str): Content to cache

##### remove(key: str)
Remove cache entry.

**Parameters:**
- `key` (str): Cache key to remove

### 7. MemoryManager Class

#### Constructor
```python
MemoryManager(max_memory_mb: int = 500)
```

**Parameters:**
- `max_memory_mb` (int): Maximum memory usage in MB

#### Methods

##### allocate_memory(component: str, size_bytes: int) -> bool
Allocate memory for component.

**Parameters:**
- `component` (str): Component name
- `size_bytes` (int): Size in bytes

**Returns:** True if allocation successful

##### deallocate_memory(component: str)
Deallocate memory for component.

**Parameters:**
- `component` (str): Component name

##### get_memory_usage() -> Dict[str, Any]
Get current memory usage.

**Returns:** Memory usage information

### 8. CursorIDEIntegration Class

#### Constructor
```python
CursorIDEIntegration(project_root: str = ".")
```

**Parameters:**
- `project_root` (str): Project root directory

#### Methods

##### install_dynamic_rules(rules_content: str, backup_existing: bool = True) -> bool
Install dynamic rules to Cursor IDE.

**Parameters:**
- `rules_content` (str): Generated rules content
- `backup_existing` (bool): Whether to backup existing rules

**Returns:** True if installation successful

**Example:**
```python
integration = CursorIDEIntegration()
success = integration.install_dynamic_rules(rules_content)
if success:
    print("Dynamic rules installed successfully")
```

##### restore_backup(backup_file: str = None) -> bool
Restore from backup.

**Parameters:**
- `backup_file` (str): Backup file path (optional)

**Returns:** True if restoration successful

### 9. ConfigurationManager Class

#### Constructor
```python
ConfigurationManager(config_path: str = "rule_config.json")
```

**Parameters:**
- `config_path` (str): Configuration file path

#### Methods

##### get_config(key: str = None) -> Any
Get configuration value.

**Parameters:**
- `key` (str): Configuration key (optional)

**Returns:** Configuration value

**Example:**
```python
config = ConfigurationManager()
max_memory = config.get_config("performance.max_memory_usage")
print(f"Max memory usage: {max_memory}")
```

##### update_config(key: str, value: Any)
Update configuration value.

**Parameters:**
- `key` (str): Configuration key
- `value` (Any): New value

**Example:**
```python
config = ConfigurationManager()
config.update_config("performance.max_memory_usage", 0.9)
```

## Configuration Reference

### 1. System Configuration (rule_config.json)

```json
{
  "version": "1.0",
  "description": "Dynamic Cursor Rules System Configuration",
  "rule_partitions": {
    "base_rules": {
      "filename": "base_rules.cursorrules",
      "priority": 10,
      "always_load": true,
      "dependencies": [],
      "conflicts": [],
      "context_requirements": {
        "project_type": ["*"],
        "task_type": ["*"],
        "session_state": ["*"]
      },
      "memory_usage_kb": 50,
      "load_time_ms": 10.0
    },
    "l0_l4_protocol": {
      "filename": "l0_l4_protocol.cursorrules",
      "priority": 8,
      "always_load": false,
      "dependencies": ["base_rules"],
      "conflicts": [],
      "context_requirements": {
        "protocol_required": ["l0_l4"],
        "task_type": ["documentation", "development"]
      },
      "memory_usage_kb": 75,
      "load_time_ms": 15.0
    },
    "ah_protocol": {
      "filename": "ah_protocol.cursorrules",
      "priority": 7,
      "always_load": false,
      "dependencies": ["base_rules"],
      "conflicts": [],
      "context_requirements": {
        "protocol_required": ["ah_protocol"],
        "task_type": ["planning", "development"]
      },
      "memory_usage_kb": 60,
      "load_time_ms": 12.0
    },
    "mcp_tools": {
      "filename": "mcp_tools.cursorrules",
      "priority": 6,
      "always_load": false,
      "dependencies": ["base_rules"],
      "conflicts": [],
      "context_requirements": {
        "protocol_required": ["mcp_tools"],
        "project_type": ["aim_os"]
      },
      "memory_usage_kb": 40,
      "load_time_ms": 8.0
    },
    "quality_standards": {
      "filename": "quality_standards.cursorrules",
      "priority": 5,
      "always_load": false,
      "dependencies": ["base_rules"],
      "conflicts": [],
      "context_requirements": {
        "task_type": ["*"],
        "complexity_level": ["medium", "high", "critical"]
      },
      "memory_usage_kb": 30,
      "load_time_ms": 5.0
    },
    "testing_protocols": {
      "filename": "testing_protocols.cursorrules",
      "priority": 4,
      "always_load": false,
      "dependencies": ["base_rules", "quality_standards"],
      "conflicts": [],
      "context_requirements": {
        "task_type": ["testing", "development"],
        "project_type": ["*"]
      },
      "memory_usage_kb": 35,
      "load_time_ms": 7.0
    },
    "documentation_standards": {
      "filename": "documentation_standards.cursorrules",
      "priority": 3,
      "always_load": false,
      "dependencies": ["base_rules"],
      "conflicts": [],
      "context_requirements": {
        "task_type": ["documentation"],
        "project_type": ["*"]
      },
      "memory_usage_kb": 25,
      "load_time_ms": 4.0
    },
    "performance_optimization": {
      "filename": "performance_optimization.cursorrules",
      "priority": 2,
      "always_load": false,
      "dependencies": ["base_rules"],
      "conflicts": [],
      "context_requirements": {
        "complexity_level": ["high", "critical"],
        "project_type": ["aim_os"]
      },
      "memory_usage_kb": 20,
      "load_time_ms": 3.0
    }
  },
  "performance": {
    "max_memory_usage": 0.8,
    "max_cpu_usage": 0.8,
    "response_time_threshold": 1000,
    "alert_enabled": true,
    "cache_size": 1000,
    "cache_ttl": 3600
  },
  "conflict_resolution": {
    "strategy": "priority_based",
    "fallback_strategy": "user_choice",
    "merge_conflicts": false,
    "log_conflicts": true
  },
  "context_analysis": {
    "ml_model_enabled": false,
    "ml_model_path": "models/context_model.pkl",
    "confidence_threshold": 0.7,
    "keyword_matching": true,
    "intent_detection": true,
    "complexity_assessment": true
  },
  "logging": {
    "level": "INFO",
    "file_path": "logs/dynamic_rules_system.log",
    "max_file_size": "10MB",
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

### 2. Keywords Configuration (keywords.json)

```json
{
  "project_type": {
    "aim_os": ["aim-os", "aether", "lucid", "mcp", "consciousness"],
    "documentation": ["documentation", "docs", "spec", "l0", "l1", "l2", "l3", "l4"],
    "testing": ["test", "testing", "validation", "audit"],
    "general": ["*"]
  },
  "task_type": {
    "development": ["implement", "code", "develop", "build", "create"],
    "documentation": ["document", "write", "spec", "l0", "l1", "l2", "l3", "l4"],
    "testing": ["test", "validate", "check", "audit", "verify"],
    "debugging": ["debug", "fix", "troubleshoot", "error"],
    "planning": ["plan", "design", "architecture", "strategy"]
  },
  "protocol_required": {
    "l0_l4": ["l0", "l1", "l2", "l3", "l4", "documentation"],
    "ah_protocol": ["a-h", "ah protocol", "idea development"],
    "lucid": ["lucid", "consciousness", "mcp"],
    "mcp_tools": ["mcp", "tools", "integration"]
  },
  "complexity_level": {
    "critical": ["critical", "urgent", "emergency", "tier 3"],
    "high": ["complex", "major", "tier 2", "architecture"],
    "low": ["simple", "minor", "tier 1", "fix"],
    "medium": ["*"]
  }
}
```

### 3. Intent Patterns Configuration (intent_patterns.json)

```json
{
  "development_task": [
    "implement.*feature",
    "build.*system",
    "create.*component",
    "develop.*functionality"
  ],
  "documentation_task": [
    "write.*documentation",
    "create.*spec",
    "document.*api",
    "l[0-4].*documentation"
  ],
  "testing_task": [
    "test.*system",
    "validate.*implementation",
    "check.*functionality",
    "audit.*code"
  ],
  "debugging_task": [
    "debug.*issue",
    "fix.*bug",
    "troubleshoot.*problem",
    "resolve.*error"
  ],
  "planning_task": [
    "plan.*architecture",
    "design.*system",
    "strategy.*development",
    "roadmap.*project"
  ]
}
```

## Data Models

### 1. ContextProfile

```python
@dataclass
class ContextProfile:
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
    raw_input: str = ""
    environment: Dict[str, Any] = None
    urgency: str = "low"
    tier_implication: int = 0
```

### 2. RuleMetadata

```python
@dataclass
class RuleMetadata:
    name: str
    description: str
    priority: int  # 1-10, higher = more important
    dependencies: List[str]  # Other partitions this depends on
    conflicts: List[str]  # Partitions this conflicts with
    context_requirements: Dict[ContextType, List[str]]  # When to load this partition
    memory_usage: int  # Estimated memory usage in KB
    load_time: float  # Estimated load time in ms
    always_load: bool = False
    filename: str = ""
```

### 3. CacheEntry

```python
@dataclass
class CacheEntry:
    content: str
    timestamp: float
    access_count: int = 0
    last_access: float = 0.0
```

### 4. Performance Metrics

```python
@dataclass
class PerformanceMetrics:
    timestamp: float
    operation: str
    duration_ms: float
    memory_usage_kb: int
    cache_hits: int
    cache_misses: int
    rules_loaded: int
    context_analysis_time_ms: float
```

## Error Handling

### 1. Error Types

#### System Errors
- `ConfigurationError`: Invalid configuration
- `RulePartitionError`: Rule partition errors
- `ContextAnalysisError`: Context analysis errors
- `MemoryError`: Memory allocation errors

#### File System Errors
- `RuleFileNotFoundError`: Rule file not found
- `BackupError`: Backup operation failed
- `PermissionError`: File permission errors

#### Integration Errors
- `CursorIntegrationError`: Cursor IDE integration errors
- `RuleInstallationError`: Rule installation failed

### 2. Error Handling Patterns

```python
try:
    loader = DynamicRuleLoader()
    context = loader.analyze_context(user_input)
    rules = loader.generate_cursor_rules(context)
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
    # Handle configuration error
except RulePartitionError as e:
    logger.error(f"Rule partition error: {e}")
    # Handle rule partition error
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle unexpected error
```

### 3. Error Recovery

```python
def generate_rules_with_retry(self, context: ContextProfile, max_retries: int = 3):
    """Generate rules with automatic retry"""
    for attempt in range(max_retries):
        try:
            return self.generate_cursor_rules(context)
        except MemoryError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Memory error, retrying: {e}")
                self.memory_manager.cleanup()
                time.sleep(1)
            else:
                raise
        except Exception as e:
            logger.error(f"Non-retryable error: {e}")
            raise
```

## Performance Optimization

### 1. Caching Strategies

#### Multi-Level Caching
```python
class MultiLevelCache:
    def __init__(self):
        self.l1_cache = {}  # In-memory cache
        self.l2_cache = {}  # Disk cache
        self.l3_cache = {}  # Network cache
    
    def get(self, key: str) -> Optional[str]:
        # Check L1 cache first
        if key in self.l1_cache:
            return self.l1_cache[key]
        
        # Check L2 cache
        if key in self.l2_cache:
            value = self.l2_cache[key]
            self.l1_cache[key] = value  # Promote to L1
            return value
        
        # Check L3 cache
        if key in self.l3_cache:
            value = self.l3_cache[key]
            self.l2_cache[key] = value  # Promote to L2
            self.l1_cache[key] = value  # Promote to L1
            return value
        
        return None
```

#### Intelligent Cache Eviction
```python
class IntelligentCacheEviction:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.access_frequency = {}
        self.access_recency = {}
    
    def evict_least_valuable(self):
        """Evict least valuable entries based on frequency and recency"""
        if len(self.cache) < self.max_size:
            return
        
        # Calculate value score for each entry
        scores = {}
        for key in self.cache:
            frequency = self.access_frequency.get(key, 0)
            recency = time.time() - self.access_recency.get(key, 0)
            scores[key] = frequency / (recency + 1)  # Avoid division by zero
        
        # Evict lowest scoring entry
        least_valuable = min(scores.keys(), key=lambda k: scores[k])
        self.remove(least_valuable)
```

### 2. Parallel Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncRuleLoader:
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def analyze_context_async(self, user_input: str, environment_data: Dict[str, Any] = None):
        """Analyze context asynchronously"""
        loop = asyncio.get_event_loop()
        
        # Run context analysis in parallel
        context_task = loop.run_in_executor(
            self.executor,
            self.context_analyzer.analyze_input,
            user_input,
            environment_data
        )
        
        # Run rule selection in parallel
        rule_selection_task = loop.run_in_executor(
            self.executor,
            self.rule_selector.select_rules,
            user_input,
            environment_data
        )
        
        # Wait for both tasks
        context, selected_rules = await asyncio.gather(
            context_task, rule_selection_task
        )
        
        return context, selected_rules
```

### 3. Memory Optimization

```python
class MemoryOptimizer:
    def __init__(self, max_memory_mb: int = 500):
        self.max_memory_mb = max_memory_mb
        self.memory_usage = {}
        self.cleanup_threshold = 0.8  # 80% of max memory
    
    def optimize_memory(self):
        """Optimize memory usage"""
        current_usage = self.get_memory_usage_mb()
        
        if current_usage > self.max_memory_mb * self.cleanup_threshold:
            self.cleanup_unused_objects()
            self.compress_caches()
            self.garbage_collect()
    
    def cleanup_unused_objects(self):
        """Clean up unused objects"""
        # Remove unused rule partitions
        for partition in list(self.rule_cache.keys()):
            if not self.is_partition_active(partition):
                del self.rule_cache[partition]
        
        # Remove old cache entries
        current_time = time.time()
        for key in list(self.cache.keys()):
            if current_time - self.cache[key].timestamp > self.cache_ttl:
                del self.cache[key]
    
    def compress_caches(self):
        """Compress cache data"""
        for key, entry in self.cache.items():
            if len(entry.content) > 1000:  # Only compress large entries
                entry.content = self.compress(entry.content)
```

## Monitoring and Observability

### 1. Metrics Collection

```python
class MetricsCollector:
    def __init__(self):
        self.metrics = {}
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
        self.timers = {}
    
    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment counter metric"""
        key = self._build_key(name, tags)
        self.counters[key] = self.counters.get(key, 0) + value
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set gauge metric"""
        key = self._build_key(name, tags)
        self.gauges[key] = value
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record histogram metric"""
        key = self._build_key(name, tags)
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(value)
    
    def start_timer(self, name: str, tags: Dict[str, str] = None):
        """Start timer"""
        key = self._build_key(name, tags)
        self.timers[key] = time.time()
    
    def stop_timer(self, name: str, tags: Dict[str, str] = None):
        """Stop timer and record duration"""
        key = self._build_key(name, tags)
        if key in self.timers:
            duration = time.time() - self.timers[key]
            self.record_histogram(f"{name}_duration", duration, tags)
            del self.timers[key]
```

### 2. Health Checks

```python
class HealthChecker:
    def __init__(self, rule_loader: DynamicRuleLoader):
        self.rule_loader = rule_loader
        self.health_checks = {
            "rule_partitions": self._check_rule_partitions,
            "context_analyzer": self._check_context_analyzer,
            "memory_usage": self._check_memory_usage,
            "cache_status": self._check_cache_status
        }
    
    def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        
        for check_name, check_func in self.health_checks.items():
            try:
                results[check_name] = {
                    "status": "healthy",
                    "details": check_func()
                }
            except Exception as e:
                results[check_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        return results
    
    def _check_rule_partitions(self) -> Dict[str, Any]:
        """Check rule partitions health"""
        partitions = list(RulePartition)
        loaded_partitions = len(self.rule_loader.loaded_partitions)
        
        return {
            "total_partitions": len(partitions),
            "loaded_partitions": loaded_partitions,
            "load_percentage": (loaded_partitions / len(partitions)) * 100
        }
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage"""
        memory_usage = self.rule_loader.memory_manager.get_memory_usage()
        
        return {
            "current_mb": memory_usage["current_mb"],
            "max_mb": memory_usage["max_mb"],
            "usage_percent": memory_usage["usage_percent"]
        }
```

### 3. Alerting

```python
class AlertManager:
    def __init__(self, alert_config: Dict[str, Any]):
        self.alert_config = alert_config
        self.alert_history = []
        self.alert_cooldown = {}
    
    def check_alerts(self, metrics: Dict[str, Any]):
        """Check metrics against alert thresholds"""
        for alert_name, alert_config in self.alert_config.items():
            if self._should_alert(alert_name, alert_config, metrics):
                self._trigger_alert(alert_name, alert_config, metrics)
    
    def _should_alert(self, alert_name: str, alert_config: Dict[str, Any], metrics: Dict[str, Any]) -> bool:
        """Check if alert should be triggered"""
        # Check cooldown
        if alert_name in self.alert_cooldown:
            if time.time() - self.alert_cooldown[alert_name] < alert_config.get("cooldown", 300):
                return False
        
        # Check threshold
        metric_name = alert_config["metric"]
        threshold = alert_config["threshold"]
        operator = alert_config["operator"]
        
        if metric_name not in metrics:
            return False
        
        value = metrics[metric_name]
        
        if operator == "gt":
            return value > threshold
        elif operator == "lt":
            return value < threshold
        elif operator == "eq":
            return value == threshold
        
        return False
    
    def _trigger_alert(self, alert_name: str, alert_config: Dict[str, Any], metrics: Dict[str, Any]):
        """Trigger alert"""
        alert = {
            "timestamp": time.time(),
            "alert_name": alert_name,
            "severity": alert_config.get("severity", "warning"),
            "message": alert_config.get("message", f"Alert triggered: {alert_name}"),
            "metrics": metrics
        }
        
        self.alert_history.append(alert)
        self.alert_cooldown[alert_name] = time.time()
        
        # Send notification
        self._send_notification(alert)
```

## Troubleshooting Guide

### 1. Common Issues

#### Issue: Rule Loading Not Working
**Symptoms:**
- No rules loaded for valid context
- Empty .cursorrules file generated

**Causes:**
- Rule partition files missing
- Context analysis failing
- Configuration errors

**Solutions:**
1. Check rule partition files exist
2. Verify context analysis output
3. Review configuration file
4. Check file permissions

#### Issue: Performance Degradation
**Symptoms:**
- Slow rule loading
- High memory usage
- System unresponsiveness

**Causes:**
- Memory leaks
- Inefficient caching
- Resource contention

**Solutions:**
1. Monitor memory usage
2. Optimize caching strategies
3. Clean up unused objects
4. Scale resources

#### Issue: Rule Conflicts
**Symptoms:**
- Conflicting rules in output
- Unexpected behavior
- Error messages

**Causes:**
- Multiple partitions with conflicting rules
- Poor conflict resolution strategy
- Configuration issues

**Solutions:**
1. Review conflict resolution strategy
2. Check partition dependencies
3. Update rule priorities
4. Test rule combinations

### 2. Debugging Tools

#### Debug Mode
```python
# Enable debug mode
loader = DynamicRuleLoader(debug=True)

# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Performance Profiling
```python
import cProfile
import pstats

# Profile system performance
profiler = cProfile.Profile()
profiler.enable()

# Run system operations
loader = DynamicRuleLoader()
context = loader.analyze_context("test input")
rules = loader.generate_cursor_rules(context)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

#### Memory Profiling
```python
import tracemalloc

# Start memory tracing
tracemalloc.start()

# Run system operations
loader = DynamicRuleLoader()
context = loader.analyze_context("test input")
rules = loader.generate_cursor_rules(context)

# Get memory snapshot
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

# Print top memory usage
for stat in top_stats[:10]:
    print(stat)
```

### 3. Log Analysis

#### Log Levels
- `DEBUG`: Detailed debugging information
- `INFO`: General information about system operation
- `WARNING`: Warning messages about potential issues
- `ERROR`: Error messages about system failures
- `CRITICAL`: Critical error messages

#### Log Analysis Script
```python
import re
from collections import Counter

def analyze_logs(log_file: str):
    """Analyze log file for patterns and issues"""
    with open(log_file, 'r') as f:
        logs = f.readlines()
    
    # Count log levels
    level_counts = Counter()
    for log in logs:
        match = re.search(r'(\w+):', log)
        if match:
            level_counts[match.group(1)] += 1
    
    print("Log Level Distribution:")
    for level, count in level_counts.most_common():
        print(f"  {level}: {count}")
    
    # Find error patterns
    error_patterns = [
        r'ERROR.*rule.*not found',
        r'ERROR.*partition.*failed',
        r'ERROR.*memory.*exhausted'
    ]
    
    for pattern in error_patterns:
        matches = [log for log in logs if re.search(pattern, log)]
        if matches:
            print(f"\nPattern '{pattern}' found {len(matches)} times:")
            for match in matches[:5]:  # Show first 5 matches
                print(f"  {match.strip()}")
```

## Security Considerations

### 1. Input Validation

```python
class InputValidator:
    def __init__(self):
        self.max_input_length = 10000
        self.allowed_characters = re.compile(r'^[a-zA-Z0-9\s\-_.,!?@#$%^&*()+={}[\]|\\:";\'<>?/~`]*$')
    
    def validate_user_input(self, user_input: str) -> bool:
        """Validate user input"""
        if len(user_input) > self.max_input_length:
            return False
        
        if not self.allowed_characters.match(user_input):
            return False
        
        return True
    
    def sanitize_input(self, user_input: str) -> str:
        """Sanitize user input"""
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', user_input)
        
        # Limit length
        if len(sanitized) > self.max_input_length:
            sanitized = sanitized[:self.max_input_length]
        
        return sanitized
```

### 2. Access Control

```python
class AccessController:
    def __init__(self, allowed_users: List[str], admin_users: List[str]):
        self.allowed_users = set(allowed_users)
        self.admin_users = set(admin_users)
        self.user_permissions = {}
    
    def check_access(self, user: str, resource: str) -> bool:
        """Check if user has access to resource"""
        if user not in self.allowed_users:
            return False
        
        if user in self.admin_users:
            return True
        
        user_perms = self.user_permissions.get(user, set())
        return resource in user_perms
    
    def grant_permission(self, user: str, resource: str):
        """Grant permission to user"""
        if user not in self.user_permissions:
            self.user_permissions[user] = set()
        self.user_permissions[user].add(resource)
```

### 3. Data Encryption

```python
from cryptography.fernet import Fernet

class DataEncryptor:
    def __init__(self, key: bytes = None):
        if key is None:
            key = Fernet.generate_key()
        self.cipher = Fernet(key)
    
    def encrypt_data(self, data: str) -> bytes:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode())
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data).decode()
```

## Deployment and Operations

### 1. Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/cache logs

# Set environment variables
ENV PYTHONPATH=/app
ENV RULE_CONFIG=/app/config/rule_config.json

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "integrate_dynamic_rules.py"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  dynamic-rules:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    environment:
      - RULE_CONFIG=/app/config/rule_config.json
    restart: unless-stopped

  monitoring:
    image: prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    depends_on:
      - dynamic-rules
```

### 2. Kubernetes Deployment

#### Deployment YAML
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dynamic-rules
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dynamic-rules
  template:
    metadata:
      labels:
        app: dynamic-rules
    spec:
      containers:
      - name: dynamic-rules
        image: dynamic-rules:latest
        ports:
        - containerPort: 8000
        env:
        - name: RULE_CONFIG
          value: "/app/config/rule_config.json"
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: data-volume
          mountPath: /app/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
      volumes:
      - name: config-volume
        configMap:
          name: dynamic-rules-config
      - name: data-volume
        persistentVolumeClaim:
          claimName: dynamic-rules-data
```

#### Service YAML
```yaml
apiVersion: v1
kind: Service
metadata:
  name: dynamic-rules-service
spec:
  selector:
    app: dynamic-rules
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 3. Monitoring and Alerting

#### Prometheus Configuration
```yaml
global:
  scrape_interval: 15s

scrape_configs:
- job_name: 'dynamic-rules'
  static_configs:
  - targets: ['dynamic-rules:8000']
  metrics_path: '/metrics'
  scrape_interval: 5s
```

#### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "Dynamic Cursor Rules System",
    "panels": [
      {
        "title": "Rule Load Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(dynamic_rules_loaded_total[5m])",
            "legendFormat": "Rules/sec"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(dynamic_rules_response_time_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "dynamic_rules_memory_usage_bytes",
            "legendFormat": "Memory Usage"
          }
        ]
      }
    ]
  }
}
```

## Best Practices

### 1. Development Best Practices

#### Code Organization
- Use clear, descriptive names for classes and methods
- Implement proper error handling and logging
- Write comprehensive unit tests
- Document all public APIs
- Follow PEP 8 style guidelines

#### Testing Strategy
- Write unit tests for all components
- Implement integration tests for workflows
- Use mocking for external dependencies
- Test error conditions and edge cases
- Maintain high test coverage (>90%)

#### Performance Considerations
- Profile code to identify bottlenecks
- Use caching to improve performance
- Implement lazy loading where appropriate
- Monitor memory usage and optimize
- Use async/await for I/O operations

### 2. Operational Best Practices

#### Monitoring
- Set up comprehensive monitoring
- Define clear alert thresholds
- Monitor both technical and business metrics
- Use dashboards for visualization
- Implement log aggregation

#### Security
- Validate all inputs
- Implement proper access controls
- Encrypt sensitive data
- Regular security audits
- Keep dependencies updated

#### Maintenance
- Regular backups of data and configuration
- Monitor system health continuously
- Plan for disaster recovery
- Document operational procedures
- Regular performance reviews

### 3. Scaling Best Practices

#### Horizontal Scaling
- Design for stateless operation
- Use load balancers
- Implement session affinity if needed
- Monitor resource utilization
- Plan for capacity growth

#### Vertical Scaling
- Monitor resource usage
- Optimize algorithms
- Use efficient data structures
- Implement caching strategies
- Profile and optimize hot paths

---
*This complete reference provides comprehensive information for implementing, deploying, and operating the Dynamic Cursor Rules System.*
