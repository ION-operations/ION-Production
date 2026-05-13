# 🔧 Daemon/RAG System - Troubleshooting Guide

**Version:** 1.0.0  
**Last Updated:** 2025-10-31  
**Status:** Comprehensive troubleshooting reference

---

## 🚨 **COMMON ISSUES & SOLUTIONS**

### **Issue 1: Tool Selection Fails**

**Symptoms:**
- `process_request()` returns empty tool list
- Error: "No tools selected"
- System can't determine required tools

**Possible Causes:**
1. Context profile incomplete
2. Tool registry not initialized
3. No matching tools for context
4. Resource constraints

**Solutions:**

```python
# 1. Check context profile completeness
context_profile = daemon.context_analyzer.analyze_context(user_input, environment)
print(f"Context Profile: {context_profile}")
# Verify: task_type, complexity, required_capabilities are set

# 2. Verify tool registry initialization
print(f"Tools Available: {len(daemon.tool_registry.get_all_tools())}")
# Should show 51 tools

# 3. Check tool selection strategy
response = daemon.process_request(user_input, environment)
print(f"Strategy Used: {response.get('strategy_used')}")
print(f"Reasoning: {response.get('reasoning')}")

# 4. Check resource availability
status = daemon.get_status()
print(f"Resources: {status.get('resource_usage')}")
```

**Prevention:**
- Always provide complete environment context
- Verify tool registry initialization
- Check resource limits before processing

---

### **Issue 2: Server Management Issues**

**Symptoms:**
- Servers fail to start
- Tool loading errors
- "Server not found" errors

**Possible Causes:**
1. MCP server configuration incorrect
2. Server script paths wrong
3. Resource limits exceeded
4. Port conflicts

**Solutions:**

```python
# 1. Check MCP server configuration
config = daemon.server_manager.get_server_config()
print(f"Server Config: {config}")

# 2. Verify server script paths
for server_id, server_info in config.items():
    script_path = server_info.get('script_path')
    if not os.path.exists(script_path):
        print(f"ERROR: Server script not found: {script_path}")

# 3. Check resource limits
status = daemon.get_status()
resource_usage = status.get('resource_usage', {})
if resource_usage.get('memory_mb', 0) > 1000:
    print("WARNING: Memory limit exceeded")

# 4. Check server health
server_status = daemon.server_manager.get_server_status()
for server_id, health in server_status.items():
    if health != "healthy":
        print(f"WARNING: Server {server_id} unhealthy: {health}")
```

**Prevention:**
- Validate MCP server configuration on startup
- Monitor resource usage continuously
- Implement health checks

---

### **Issue 3: Performance Issues**

**Symptoms:**
- Response times >400ms
- Tool selection >50ms
- High CPU/memory usage

**Possible Causes:**
1. Inefficient tool selection strategy
2. Too many tools selected
3. RAG system overhead
4. Resource contention

**Solutions:**

```python
# 1. Check performance metrics
status = daemon.get_status()
performance = status.get('performance_metrics', {})
print(f"Avg Response Time: {performance.get('avg_response_time_ms')}ms")
print(f"Avg Tool Selection: {performance.get('avg_tool_selection_ms')}ms")

# 2. Optimize tool selection strategy
config = DaemonConfig(
    max_tools=40,
    tool_selection_strategy="PERFORMANCE"  # Use performance-optimized strategy
)
daemon = DaemonRAGSystem(config)

# 3. Reduce tool count
# Modify selection to prioritize fewer, more relevant tools

# 4. Check RAG system overhead
rag_stats = daemon.get_rag_statistics()
print(f"RAG Query Time: {rag_stats.get('avg_query_time_ms')}ms")
# If high, consider disabling RAG temporarily for performance testing
```

**Prevention:**
- Monitor performance continuously
- Use performance-optimized strategies
- Set resource limits appropriately

---

### **Issue 4: Learning System Issues**

**Symptoms:**
- Learning not improving selections
- Patterns not stored
- Outcomes not tracked

**Possible Causes:**
1. Learning disabled
2. Pattern storage failing
3. Outcome tracking broken
4. RAG system not updating

**Solutions:**

```python
# 1. Check learning enabled
config = daemon.config
if not config.learning_enabled:
    print("WARNING: Learning is disabled")

# 2. Verify pattern storage
rag_stats = daemon.get_rag_statistics()
print(f"Patterns Stored: {rag_stats.get('patterns_stored', 0)}")
print(f"Pattern Retrievals: {rag_stats.get('pattern_retrievals', 0)}")

# 3. Check outcome tracking
learning_status = daemon.learning_system.get_learning_status()
print(f"Outcomes Tracked: {learning_status.get('outcomes_tracked', 0)}")
print(f"Improvement Rate: {learning_status.get('improvement_rate', 0)}")

# 4. Force learning update
daemon.learning_system.update_from_outcomes(recent_outcomes)
```

**Prevention:**
- Enable learning in configuration
- Monitor learning metrics
- Validate pattern storage

---

### **Issue 5: Resource Management Issues**

**Symptoms:**
- Memory leaks
- CPU spikes
- Server crashes
- Resource limits exceeded

**Possible Causes:**
1. Resources not released
2. Memory leaks in components
3. Thread leaks
4. Server processes not cleaned up

**Solutions:**

```python
# 1. Monitor resource usage
import psutil
import os

process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
cpu_percent = process.cpu_percent(interval=1)

print(f"Memory: {memory_mb}MB")
print(f"CPU: {cpu_percent}%")

# 2. Check server processes
server_status = daemon.server_manager.get_server_status()
for server_id, status in server_status.items():
    if status == "running":
        # Check process resources
        server_process = daemon.server_manager.get_server_process(server_id)
        if server_process:
            server_memory = server_process.memory_info().rss / 1024 / 1024
            print(f"Server {server_id} Memory: {server_memory}MB")

# 3. Force cleanup
daemon.resource_manager.cleanup_resources()
daemon.server_manager.cleanup_servers()

# 4. Restart daemon
daemon.stop()
daemon.start()
```

**Prevention:**
- Implement proper resource cleanup
- Monitor resource usage continuously
- Set appropriate resource limits

---

## 🔍 **DEBUGGING TECHNIQUES**

### **Enable Debug Logging**

```python
import logging

# Set debug level
logging.basicConfig(level=logging.DEBUG)

# Or configure daemon with debug logging
config = DaemonConfig(log_level="DEBUG")
daemon = DaemonRAGSystem(config)
```

### **Inspect System State**

```python
# Get complete system status
status = daemon.get_status()
print(json.dumps(status, indent=2))

# Check component states
print(f"Tool Registry: {daemon.tool_registry.get_tool_statistics()}")
print(f"Context Analyzer: {daemon.context_analyzer.get_statistics()}")
print(f"Tool Selector: {daemon.tool_selector.get_selection_statistics()}")
print(f"RAG System: {daemon.get_rag_statistics()}")
print(f"Server Manager: {daemon.server_manager.get_server_status()}")
print(f"Performance Monitor: {daemon.performance_monitor.get_performance_summary()}")
print(f"Learning System: {daemon.learning_system.get_learning_status()}")
print(f"Resource Manager: {daemon.resource_manager.get_resource_usage()}")
```

### **Trace Request Flow**

```python
# Enable request tracing
config = DaemonConfig(
    enable_request_tracing=True,
    trace_file="daemon_trace.log"
)
daemon = DaemonRAGSystem(config)

# Process request with tracing
response = daemon.process_request(user_input, environment)

# Review trace file
with open("daemon_trace.log", "r") as f:
    print(f.read())
```

---

## 📊 **PERFORMANCE TROUBLESHOOTING**

### **Identify Bottlenecks**

```python
# Get detailed performance breakdown
performance = daemon.performance_monitor.get_performance_breakdown()

print(f"Context Analysis: {performance['context_analysis_ms']}ms")
print(f"Tool Selection: {performance['tool_selection_ms']}ms")
print(f"Server Management: {performance['server_management_ms']}ms")
print(f"RAG Query: {performance['rag_query_ms']}ms")
print(f"Total: {performance['total_ms']}ms")

# Identify slowest component
slowest = max(performance.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0)
print(f"Slowest Component: {slowest[0]} ({slowest[1]}ms)")
```

### **Optimize Tool Selection**

```python
# Use performance-optimized strategy
config = DaemonConfig(
    tool_selection_strategy="PERFORMANCE",
    max_tools=30  # Reduce from 40 for better performance
)

# Or use capability-focused strategy
config = DaemonConfig(
    tool_selection_strategy="CAPABILITY",
    max_tools=40
)
```

---

## 🛡️ **ERROR HANDLING**

### **Handle Component Failures**

```python
try:
    response = daemon.process_request(user_input, environment)
except Exception as e:
    print(f"Error: {e}")
    # System should handle gracefully
    # Check error logs for details
    status = daemon.get_status()
    if status['status'] == 'error':
        print(f"Error Details: {status.get('error_details')}")
```

### **Recovery Procedures**

```python
# Check if daemon is healthy
status = daemon.get_status()
if status['status'] != 'running':
    # Restart daemon
    daemon.stop()
    daemon.start()

# Verify components
if not daemon.tool_registry:
    daemon.tool_registry = ToolRegistry()
if not daemon.context_analyzer:
    daemon.context_analyzer = ContextAnalysisEngine()
# ... initialize other components
```

---

## 📚 **ADDITIONAL RESOURCES**

- **README:** `daemon_rag_system/README.md` - Complete implementation guide
- **Architecture:** `knowledge_architecture/systems/daemon_rag_system/L2_architecture.md`
- **API Docs:** `daemon_rag_system/API_DOCUMENTATION.md`
- **Tests:** `daemon_rag_system/test_daemon_rag_system.py` - Example usage

---

## 💡 **BEST PRACTICES**

1. **Monitor Continuously:** Use performance monitoring to catch issues early
2. **Validate Configuration:** Check MCP server configs on startup
3. **Handle Errors Gracefully:** Implement proper error handling
4. **Resource Management:** Monitor and limit resource usage
5. **Learning Enabled:** Keep learning enabled for continuous improvement
6. **Debug Logging:** Enable debug logging when troubleshooting

---

**Need More Help?** Check the comprehensive README or architecture docs! 💙

