# Daemon/RAG System Templates

**Date:** 2025-10-31  
**Status:** ✅ COMPLETE  
**Purpose:** Standardized templates for Daemon/RAG System operations  
**System:** Daemon/RAG System

---

## 📋 **TEMPLATE OVERVIEW**

This document provides standardized templates for Daemon/RAG System operations, ensuring consistency, completeness, and quality across all tool selection, server management, and RAG operations.

---

## 🎯 **CORE TEMPLATES**

### **1. Tool Selection Request Template**

```json
{
  "request_id": "req_YYYY-MM-DD_HHMMSS",
  "timestamp": "2025-10-31T10:47:14.073007",
  "query": "User query or request",
  "context": {
    "current_file": "file_path",
    "active_function": "function_name",
    "recent_messages": ["message1", "message2"],
    "session_id": "session_identifier",
    "user_id": "user_identifier"
  },
  "environment": {
    "system_resources": {
      "cpu_usage_percent": 45.2,
      "memory_usage_mb": 1024,
      "available_tools": 40
    },
    "server_status": {
      "active_servers": 2,
      "server_load": 0.65
    }
  },
  "requirements": {
    "max_tools": 40,
    "max_response_time_ms": 400,
    "required_capabilities": ["memory", "analysis"]
  }
}
```

---

### **2. Tool Selection Response Template**

```json
{
  "request_id": "req_YYYY-MM-DD_HHMMSS",
  "timestamp": "2025-10-31T10:47:14.073007",
  "success": true,
  "selected_tools": [
    {
      "tool_id": "store_memory",
      "name": "store_memory",
      "category": "memory",
      "relevance_score": 0.98,
      "reasoning": "Query indicates memory storage requirement"
    }
  ],
  "context_profile": {
    "current_task": "memory_management",
    "confidence_score": 0.95,
    "complexity_level": "medium"
  },
  "selection_result": {
    "reasoning": "Query indicates memory storage and retrieval. Selected tools are highly relevant.",
    "relevance_scores": {
      "store_memory": 0.98,
      "get_memory_stats": 0.92,
      "retrieve_context": 0.90
    }
  },
  "performance_metrics": {
    "tool_selection_time_ms": 15.3,
    "context_analysis_time_ms": 45.2,
    "rag_query_time_ms": 12.8,
    "total_request_time_ms": 68.7
  },
  "ah_protocol_data": {
    "intent_profile": {},
    "confidence_packet": {},
    "context_map": {}
  }
}
```

---

### **3. Server Management Template**

```json
{
  "server_id": "server_YYYY-MM-DD_HHMMSS",
  "timestamp": "2025-10-31T10:47:14.073007",
  "action": "create|start|stop|restart|status",
  "server_config": {
    "server_type": "mcp_server",
    "tools": ["tool1", "tool2", "tool3"],
    "max_tools": 40,
    "resource_limits": {
      "memory_mb": 2048,
      "cpu_percent": 80
    }
  },
  "status": {
    "server_state": "running|stopped|starting|stopping",
    "active_tools": 15,
    "resource_usage": {
      "memory_mb": 1024,
      "cpu_percent": 45.2
    },
    "health_status": "healthy|degraded|unhealthy"
  },
  "management_result": {
    "success": true,
    "message": "Server created successfully",
    "warnings": [],
    "errors": []
  }
}
```

---

### **4. RAG Query Template**

```json
{
  "query_id": "query_YYYY-MM-DD_HHMMSS",
  "timestamp": "2025-10-31T10:47:14.073007",
  "query_text": "User query for tool selection",
  "query_type": "tool_selection|context_analysis|pattern_recognition",
  "embedding": {
    "vector": [0.123, 0.456, ...],
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "dimension": 384
  },
  "vector_search": {
    "index_name": "mcp_tools_index",
    "top_k": 10,
    "similarity_threshold": 0.75
  },
  "results": [
    {
      "tool_id": "store_memory",
      "similarity_score": 0.98,
      "reasoning": "Highly relevant to query"
    }
  ],
  "learning_update": {
    "pattern_type": "query_tool_pattern",
    "success": true,
    "outcome": "tool_selected"
  }
}
```

---

### **5. Performance Metrics Template**

```json
{
  "metrics_id": "metrics_YYYY-MM-DD_HHMMSS",
  "timestamp": "2025-10-31T10:47:14.073007",
  "time_period": "last_hour|last_day|last_week",
  "tool_selection": {
    "total_requests": 124,
    "avg_selection_time_ms": 15.3,
    "p95_selection_time_ms": 28.5,
    "p99_selection_time_ms": 45.2,
    "success_rate": 0.98
  },
  "context_analysis": {
    "total_analyses": 124,
    "avg_analysis_time_ms": 45.2,
    "p95_analysis_time_ms": 78.3,
    "p99_analysis_time_ms": 120.5
  },
  "rag_system": {
    "total_queries": 124,
    "avg_query_time_ms": 12.8,
    "avg_similarity_score": 0.85,
    "cache_hit_rate": 0.65
  },
  "server_management": {
    "total_servers": 2,
    "avg_server_uptime_percent": 99.5,
    "total_server_restarts": 0,
    "avg_server_load": 0.65
  },
  "learning_system": {
    "total_patterns_learned": 150,
    "pattern_accuracy": 0.92,
    "learning_updates": 124
  },
  "resource_usage": {
    "avg_cpu_percent": 45.2,
    "avg_memory_mb": 1024,
    "peak_cpu_percent": 78.5,
    "peak_memory_mb": 1536
  }
}
```

---

### **6. Error Handling Template**

```json
{
  "error_id": "error_YYYY-MM-DD_HHMMSS",
  "timestamp": "2025-10-31T10:47:14.073007",
  "error_type": "tool_selection_error|server_error|rag_error|resource_error",
  "severity": "low|medium|high|critical",
  "error_details": {
    "error_code": "TOOL_SELECTION_TIMEOUT",
    "error_message": "Tool selection exceeded timeout threshold",
    "error_context": {
      "request_id": "req_YYYY-MM-DD_HHMMSS",
      "query": "User query",
      "selected_tools": []
    },
    "stack_trace": "..."
  },
  "recovery_action": {
    "action_taken": "fallback_to_default_tools",
    "success": true,
    "fallback_tools": ["tool1", "tool2"]
  },
  "prevention": {
    "recommendations": [
      "Increase timeout threshold",
      "Optimize tool selection algorithm",
      "Add caching for common queries"
    ]
  }
}
```

---

### **7. Learning Update Template**

```json
{
  "learning_id": "learning_YYYY-MM-DD_HHMMSS",
  "timestamp": "2025-10-31T10:47:14.073007",
  "pattern_type": "query_tool_pattern|tool_usage_pattern|performance_pattern",
  "pattern_data": {
    "query": "User query",
    "selected_tools": ["tool1", "tool2"],
    "outcome": "success|failure",
    "performance_metrics": {
      "response_time_ms": 68.7,
      "accuracy": 0.95
    }
  },
  "learning_adjustment": {
    "tool_weights": {
      "tool1": 0.98,
      "tool2": 0.92
    },
    "context_patterns": {
      "memory_management": ["store_memory", "get_memory_stats"]
    },
    "confidence_adjustment": 0.02
  },
  "validation": {
    "pattern_validated": true,
    "validation_score": 0.92,
    "outcome": "pattern_accepted"
  }
}
```

---

## 🔧 **USAGE GUIDELINES**

### **When to Use Each Template**

1. **Tool Selection Request Template:** Use when processing a new user request that requires tool selection
2. **Tool Selection Response Template:** Use when returning tool selection results
3. **Server Management Template:** Use for all server lifecycle operations
4. **RAG Query Template:** Use for all RAG system queries and vector searches
5. **Performance Metrics Template:** Use for periodic performance reporting
6. **Error Handling Template:** Use for all error conditions and recovery actions
7. **Learning Update Template:** Use for all learning system updates and pattern recognition

### **Template Validation**

All templates should:
- Include required fields
- Validate data types
- Enforce constraints (e.g., max_tools <= 40)
- Include timestamps for traceability
- Include request/response IDs for correlation

---

## 📊 **INTEGRATION WITH STANDARDS**

These templates integrate with:
- **L0-L6 Documentation Standard:** Templates documented in L3 detailed guide
- **Validation Framework:** Templates validated through validation checklist
- **System Maps:** Templates referenced in system map
- **A-H Protocol:** Templates include A-H Protocol data structures

---

## ✅ **COMPLIANCE STATUS**

- ✅ Templates documented
- ✅ Templates integrated with system
- ✅ Templates validated
- ✅ Templates used in code

---

**Status:** Complete and Production-Ready ✅

