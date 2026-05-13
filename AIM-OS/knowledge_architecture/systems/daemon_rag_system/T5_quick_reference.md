---
id: "daemon_rag_system_T5_quick_reference"
system: "daemon_rag_system"
component: null
level: "T5"
type: "quick_reference"
title: "Daemon/RAG System Quick Reference"
description: "Quick API reference for Daemon/RAG System"
audience: "developers, operators"
confidence_threshold: 0.80
token_cost: 800
word_count: 800
created: "2025-11-05T00:00:00Z"
updated: "2025-11-05T00:00:00Z"
author: "aether"
status: "complete"
tags: ["daemon_rag", "quick-reference", "api", "t5", "transitional"]
dependencies: ["daemon_rag_system_T3_detailed", "daemon_rag_system_T4_complete"]
related_docs: ["daemon_rag_system_T6_source_code_reference"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Daemon/RAG System – T5 Quick Reference

**Quick API guide for developers using Daemon/RAG System**

---

## 🚀 **QUICK START**

### **Initialize Daemon**

```python
from daemon_rag_system.daemon_rag_system import DaemonRAGSystem, DaemonConfig

# Create with defaults
daemon = DaemonRAGSystem()
daemon.start()

# Or with custom config
config = DaemonConfig(
    max_tools=40,
    learning_enabled=True,
    performance_monitoring_enabled=True,
    log_level="INFO"
)
daemon = DaemonRAGSystem(config)
daemon.start()
```

### **Process User Request**

```python
# Basic usage
result = daemon.process_request(
    user_input="Help me implement authentication",
    environment={
        'current_file': 'auth.py',
        'project_type': 'python',
        'task_complexity': 'medium'
    }
)

# Returns:
{
    'selected_tools': ['store_memory', 'retrieve_memory', 'track_confidence', ...],  # 40 tools
    'servers_loaded': ['core_aimos', 'scor', 'autonomous_protocol'],
    'selection_strategy': 'BALANCED',
    'confidence_score': 0.85,
    'response_time_ms': 245
}
```

### **Get Status**

```python
status = daemon.get_status()

# Returns:
{
    'status': 'RUNNING',
    'total_requests': 1547,
    'successful_requests': 1523,
    'average_response_time_ms': 234,
    'active_servers': 8,
    'loaded_tools': 40,
    'memory_usage_mb': 412,
    'cpu_usage_percent': 23.4
}
```

---

## 📖 **CORE API**

### **DaemonRAGSystem Class**

#### **Initialization**

```python
daemon = DaemonRAGSystem(config: DaemonConfig = None)
```

**Config Options:**
- `max_tools: int = 40` - Tool limit (Cursor constraint)
- `context_analysis_timeout_ms: int = 100` - Context analysis budget
- `tool_selection_timeout_ms: int = 50` - Selection budget
- `learning_enabled: bool = True` - Enable learning
- `performance_monitoring_enabled: bool = True` - Enable monitoring
- `log_level: str = "INFO"` - Logging level

#### **Main Methods**

**start() → bool**
- Starts daemon system
- Initializes all subsystems
- Begins performance monitoring
- Returns `True` if successful

**stop() → bool**
- Stops daemon system gracefully
- Shuts down all servers
- Saves learning state
- Returns `True` if successful

**process_request(user_input: str, environment: Dict = None) → Dict**
- Analyzes context
- Selects optimal 40 tools
- Loads appropriate servers
- Tracks performance
- Learns from outcome
- Returns selection result

**get_status() → DaemonStatus**
- Returns current daemon status
- Includes metrics and health info

**get_metrics() → DaemonMetrics**
- Returns detailed performance metrics
- Request counts, timing, resource usage

---

## 🔧 **SELECTION STRATEGIES**

### **Built-in Strategies:**

**BALANCED (default)**
```python
# General-purpose, works for most tasks
# Balances performance, capability, reliability
result = daemon.process_request(user_input, {'strategy': 'BALANCED'})
```

**PERFORMANCE**
```python
# Speed-critical tasks
# Prioritizes fastest tools
result = daemon.process_request(user_input, {'strategy': 'PERFORMANCE'})
```

**CAPABILITY**
```python
# Feature-rich tasks
# Prioritizes most capable tools
result = daemon.process_request(user_input, {'strategy': 'CAPABILITY'})
```

**LEARNING**
```python
# Pattern-based tasks
# Uses RAG to find similar successful contexts
result = daemon.process_request(user_input, {'strategy': 'LEARNING'})
```

---

## 📊 **MONITORING & DEBUGGING**

### **Performance Metrics**

```python
metrics = daemon.get_metrics()

print(f"Total requests: {metrics.total_requests}")
print(f"Success rate: {metrics.successful_requests / metrics.total_requests}")
print(f"Avg response: {metrics.average_response_time_ms}ms")
print(f"Memory: {metrics.memory_usage_mb}MB")
print(f"CPU: {metrics.cpu_usage_percent}%")
```

### **Server Status**

```python
servers = daemon.server_manager.get_server_status()

for server_id, status in servers.items():
    print(f"{server_id}: {status['state']} ({status['loaded_tools']} tools)")
```

### **Learning Insights**

```python
patterns = daemon.learning_system.get_top_patterns(limit=5)

for pattern in patterns:
    print(f"Pattern: {pattern['context_type']}")
    print(f"Success rate: {pattern['success_rate']}")
    print(f"Recommended tools: {pattern['tools'][:5]}...")
```

---

## ⚡ **COMMON TASKS**

### **Task 1: Code Implementation**

```python
result = daemon.process_request(
    "Implement user authentication with JWT",
    environment={
        'task_type': 'implementation',
        'language': 'python',
        'complexity': 'medium',
        'systems_needed': ['CMC', 'VIF', 'SDF-CVF']
    }
)

# Uses: store_memory, track_confidence, check_invariant, etc.
```

### **Task 2: Autonomous Operation**

```python
result = daemon.process_request(
    "Run autonomous documentation work",
    environment={
        'task_type': 'autonomous',
        'mode': 'self_directed',
        'duration_hours': 4
    }
)

# Uses: autonomous protocol tools, timeline tools, goal tools
```

### **Task 3: Research & Analysis**

```python
result = daemon.process_request(
    "Analyze system performance and suggest optimizations",
    environment={
        'task_type': 'analysis',
        'focus': 'performance',
        'depth': 'deep'
    }
)

# Uses: retrieve_memory, get_consciousness_metrics, ARD tools
```

---

## 🐛 **TROUBLESHOOTING**

### **Issue: Slow Response Times (>400ms)**

```python
# Check component timing
metrics = daemon.get_metrics()
print(f"Context analysis: {metrics.context_analysis_time_ms}ms")
print(f"Tool selection: {metrics.tool_selection_time_ms}ms")
print(f"Server management: {metrics.server_management_time_ms}ms")

# If context analysis slow → Reduce environment data
# If tool selection slow → Use simpler strategy
# If server management slow → Reduce server switching
```

### **Issue: Poor Tool Selections**

```python
# Check learning patterns
patterns = daemon.learning_system.get_patterns_for_context(
    context_type='implementation'
)

# If patterns empty → Not enough learning data
# If patterns stale → Clear old patterns
# Solution: Use LEARNING strategy for better results
```

### **Issue: Memory Usage High**

```python
# Check resource usage
resources = daemon.resource_manager.get_resource_usage()
print(f"Pattern cache: {resources['pattern_cache_mb']}MB")
print(f"Server memory: {resources['server_memory_mb']}MB")

# Solution: Clear pattern cache or reduce server count
daemon.rag_system.clear_old_patterns(older_than_days=7)
```

---

## 🔗 **INTEGRATION EXAMPLES**

### **With CMC (Memory)**

```python
# Daemon automatically includes CMC tools when needed
result = daemon.process_request(
    "Store this important insight about architecture",
    environment={'task_type': 'memory_operation'}
)

# Daemon selects: store_memory, create_snapshot, add_timeline_entry
```

### **With Cursor Extension**

```python
# Via HTTP endpoint
import requests

response = requests.post(
    'http://localhost:5002/daemon/select-tools',
    json={
        'user_input': 'Debug this error',
        'environment': {'file': 'main.py', 'error_type': 'runtime'}
    }
)

tools = response.json()['selected_tools']
```

### **With MCP Protocol**

```python
# Via MCP server wrapper
# Daemon exposed as MCP tool itself via daemon_rag_mcp_server.py

# Cursor calls:
mcp.call_tool('daemon_select_tools', {
    'input': 'Implement feature X',
    'context': {...}
})
```

---

## 📚 **FURTHER READING**

- **T0 Executive:** Quick overview (100 words)
- **T1 Overview:** System purpose and concepts (500 words)
- **T2 Architecture:** Complete architecture (2,000 words)
- **T3 Detailed:** Implementation guide (10,000 words)
- **T4 Complete:** Full reference (15,000 words)
- **T6 Source Code:** Code navigation (when created)
- **System Map:** `system.map.lucid.json5`

---

## 🎯 **KEY PERFORMANCE TARGETS**

```
Context Analysis: < 100ms
Tool Selection: < 50ms
Server Management: < 200ms
Total Response: < 400ms (strict)
Success Rate: > 95%
Learning Accuracy: > 85%
```

---

**Status:** Quick reference complete  
**Next:** T6 Source Code Reference  
**Use:** For rapid development and debugging

