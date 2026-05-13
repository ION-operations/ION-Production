# Chronos - TCS/APOE Integration Documentation

**Agent:** Chronos (TCS System Specialist)  
**Date:** 2025-01-27  
**Status:** Complete  
**Related Systems:** TCS (Timeline Context System), APOE (AI-Powered Orchestration Engine)  
**Collaborating With:** @Alex (APOE), @Aether, @Codex  
**Priority:** Medium - Integration Documentation

---

## 📋 **EXECUTIVE SUMMARY**

**Integration Overview:**
TCS provides timeline tracking for APOE orchestration events. APOE creates timeline entries for plan execution, step execution, gate evaluations, budget milestones, DEPP modifications, and errors. TCS enables APOE to track execution history, restore execution state, and analyze performance patterns.

**Integration Pattern:**
- **TCS → APOE:** Timeline entry creation for orchestration events
- **APOE → TCS:** Execution context, plan/step metadata, orchestration state
- **Integration Method:** MCP tools (`mcp_lucid-mcp_add_timeline_entry`, `mcp_lucid-mcp_get_timeline_entries`)

**Status:** Integration API documented, implementation recommendations provided, ready for Phase 1 implementation

---

## 🔗 **INTEGRATION OVERVIEW**

### **TCS → APOE Flow**
```
APOE Orchestration Event
    ↓
APOE Creates Timeline Entry (via MCP tool)
    ↓
TCS Stores Entry in CMC (bitemporal record)
    ↓
TCS Indexes Entry in HHNI (temporal search)
    ↓
TCS Makes Entry Available for Queries
```

### **APOE → TCS Flow**
```
APOE Needs Execution History
    ↓
APOE Queries Timeline (via MCP tool)
    ↓
TCS Returns Timeline Entries
    ↓
APOE Reconstructs Execution State
```

---

## 📋 **TCS TIMELINE API**

### **1. Timeline Entry Creation**

**Method:** MCP Tool `mcp_lucid-mcp_add_timeline_entry`

**Signature:**
```python
result = await mcp_client.call_tool(
    "mcp_lucid-mcp_add_timeline_entry",
    {
        "event_type": str,        # Event type (e.g., "apoe_plan_start")
        "title": str,             # Entry title (required)
        "description": str,       # Entry description (required)
        "context_data": Dict,     # Context data (recommended)
        "tags": List[str],        # Tags for indexing (recommended)
        "metadata": Dict,         # Metadata for correlation (recommended)
        "emotional_context": Dict, # Emotional context (optional)
        "next_steps": List[str],  # Next steps (optional)
        "related_files": List[str] # Related files (optional)
    }
)
```

**Returns:**
```python
{
    "entry_id": str,           # Timeline entry ID
    "timestamp": str,          # ISO 8601 timestamp
    "prompt_id": str,          # Prompt ID
    "atom_id": str,            # CMC atom ID
    "indexed": bool            # HHNI indexing status
}
```

**Performance:**
- **Latency:** ~15-30ms per entry (including CMC storage + HHNI indexing)
- **Throughput:** 100+ entries/second (typical APOE execution rates)
- **Batching:** Optional (only for >1000 events/second)

### **2. Timeline Query**

**Method:** MCP Tool `mcp_lucid-mcp_get_timeline_entries`

**Signature:**
```python
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "event_types": List[str],     # Filter by event types (optional)
        "start_time": str,            # ISO 8601 start time (optional)
        "end_time": str,              # ISO 8601 end time (optional)
        "tags": List[str],            # Filter by tags (optional)
        "metadata_filter": Dict,      # Filter by metadata (optional)
        "limit": int,                 # Limit results (default: 100, max: 1000)
        "sort_by": str,               # Sort field ("timestamp", "entry_id")
        "order": str                  # Sort order ("asc", "desc")
    }
)
```

**Returns:**
```python
{
    "entries": [
        {
            "entry_id": str,
            "event_type": str,
            "title": str,
            "description": str,
            "timestamp": str,
            "context_data": Dict,
            "metadata": Dict,
            "tags": List[str]
        },
        ...
    ],
    "total": int,
    "has_more": bool
}
```

**Performance:**
- **Latency:** ~50-200ms per query (depending on complexity)
- **Simple Queries:** ~50-100ms (by execution_id, plan_id, single event type)
- **Complex Queries:** ~100-200ms (time-range + multiple event types + tags + metadata filters)

---

## 📋 **APOE TIMELINE ENTRY TYPES**

### **1. Plan Execution Events**

**Event Types:**
- `apoe_plan_start` - Plan execution started
- `apoe_plan_complete` - Plan execution completed

**Example:**
```python
# Plan start
await mcp_client.call_tool(
    "mcp_lucid-mcp_add_timeline_entry",
    {
        "event_type": "apoe_plan_start",
        "title": f"Plan {plan_name} Execution Started",
        "description": f"Plan execution started: {plan.description}",
        "context_data": {
            "plan_name": plan.name,
            "plan_id": plan.id,
            "execution_id": execution_id,
            "total_steps": len(plan.steps),
            "roles": plan.roles,
            "budget": {
                "tokens": plan.budget.tokens,
                "time_seconds": plan.budget.time_seconds,
                "consumed": 0,
                "remaining": plan.budget.tokens
            }
        },
        "tags": ["apoe", "plan_execution", "start"],
        "metadata": {
            "correlation_id": execution_id,
            "plan_id": plan.id,
            "execution_id": execution_id
        }
    }
)

# Plan completion
await mcp_client.call_tool(
    "mcp_lucid-mcp_add_timeline_entry",
    {
        "event_type": "apoe_plan_complete",
        "title": f"Plan {plan_name} Execution Completed",
        "description": f"Plan execution completed: {plan.description}",
        "context_data": {
            "plan_name": plan.name,
            "plan_id": plan.id,
            "execution_id": execution_id,
            "success": execution_result.success,
            "completed_steps": execution_result.completed_steps,
            "failed_steps": execution_result.failed_steps,
            "total_duration_seconds": execution_result.duration,
            "effectiveness_score": execution_result.effectiveness_score
        },
        "tags": ["apoe", "plan_execution", "complete"],
        "metadata": {
            "correlation_id": execution_id,
            "plan_id": plan.id,
            "execution_id": execution_id
        }
    }
)
```

### **2. Step Execution Events**

**Event Types:**
- `apoe_step_start` - Step execution started
- `apoe_step_complete` - Step execution completed

**Example:**
```python
# Step start
await mcp_client.call_tool(
    "mcp_lucid-mcp_add_timeline_entry",
    {
        "event_type": "apoe_step_start",
        "title": f"Step {step_name} Started",
        "description": f"Step {step_id} execution started",
        "context_data": {
            "step_id": step_id,
            "step_name": step_name,
            "plan_id": plan_id,
            "execution_id": execution_id,
            "role": role,
            "budget": {
                "tokens": step_budget.tokens,
                "time_seconds": step_budget.time_seconds,
                "consumed": 0,
                "remaining": step_budget.tokens
            }
        },
        "tags": ["apoe", "step_execution", "start", role],
        "metadata": {
            "correlation_id": execution_id,
            "plan_id": plan_id,
            "step_id": step_id,
            "execution_id": execution_id
        }
    }
)

# Step completion
await mcp_client.call_tool(
    "mcp_lucid-mcp_add_timeline_entry",
    {
        "event_type": "apoe_step_complete",
        "title": f"Step {step_name} Completed",
        "description": f"Step {step_id} execution completed",
        "context_data": {
            "step_id": step_id,
            "step_name": step_name,
            "plan_id": plan_id,
            "execution_id": execution_id,
            "status": "completed",
            "confidence": 0.95,
            "duration_seconds": 3.2,
            "outputs": {
                "valid": True,
                "format": "correct"
            }
        },
        "tags": ["apoe", "step_execution", "complete", role],
        "metadata": {
            "correlation_id": execution_id,
            "plan_id": plan_id,
            "step_id": step_id,
            "execution_id": execution_id,
            "vif_witness_id": witness_id  # Link to VIF witness if available
        }
    }
)
```

### **3. Gate Evaluation Events**

**Event Type:**
- `apoe_gate_evaluation` - Gate evaluation result

**Example:**
```python
await mcp_client.call_tool(
    "mcp_lucid-mcp_add_timeline_entry",
    {
        "event_type": "apoe_gate_evaluation",
        "title": f"Gate {gate_name} Evaluated",
        "description": f"Gate {gate_id} evaluation: {result}",
        "context_data": {
            "gate_id": gate_id,
            "gate_name": gate_name,
            "step_id": step_id,
            "plan_id": plan_id,
            "execution_id": execution_id,
            "gate_type": "quality",
            "condition": "output.valid == True",
            "result": "passed",
            "confidence": 0.95
        },
        "tags": ["apoe", "gate_evaluation", "quality"],
        "metadata": {
            "correlation_id": execution_id,
            "plan_id": plan_id,
            "step_id": step_id,
            "gate_id": gate_id
        }
    }
)
```

### **4. Budget Consumption Events**

**Event Type:**
- `apoe_budget_milestone` - Budget consumption milestone

**Example:**
```python
await mcp_client.call_tool(
    "mcp_lucid-mcp_add_timeline_entry",
    {
        "event_type": "apoe_budget_milestone",
        "title": f"Budget {budget_type} Milestone: {percentage}%",
        "description": f"Budget consumption milestone reached",
        "context_data": {
            "plan_id": plan_id,
            "execution_id": execution_id,
            "budget_type": "tokens",
            "consumed": 5000,
            "limit": 10000,
            "percentage": 50.0,
            "warning_threshold": 80.0
        },
        "tags": ["apoe", "budget", "milestone"],
        "metadata": {
            "correlation_id": execution_id,
            "plan_id": plan_id
        }
    }
)
```

### **5. DEPP Modification Events**

**Event Type:**
- `apoe_depp_modification` - DEPP modification event

**Example:**
```python
await mcp_client.call_tool(
    "mcp_lucid-mcp_add_timeline_entry",
    {
        "event_type": "apoe_depp_modification",
        "title": f"DEPP Modification: {modification_type}",
        "description": f"DEPP modified based on evidence",
        "context_data": {
            "modification_id": modification_id,
            "plan_id": plan_id,
            "execution_id": execution_id,
            "modification_type": "add_step",
            "target_step_id": step_id,
            "reason": "Low historical success rate - adding verification",
            "confidence": 0.75,
            "evidence_source": "seg_effectiveness_patterns"
        },
        "tags": ["apoe", "depp", "modification"],
        "metadata": {
            "correlation_id": execution_id,
            "plan_id": plan_id,
            "seg_evidence_id": evidence_id  # Link to SEG evidence node
        }
    }
)
```

### **6. Error Events**

**Event Type:**
- `apoe_error` - Error event

**Example:**
```python
await mcp_client.call_tool(
    "mcp_lucid-mcp_add_timeline_entry",
    {
        "event_type": "apoe_error",
        "title": f"Error: {error_type}",
        "description": f"Error occurred: {error_message}",
        "context_data": {
            "error_type": "step_failure",
            "step_id": step_id,
            "plan_id": plan_id,
            "execution_id": execution_id,
            "error_message": "Validation failed: invalid format",
            "error_code": "VALIDATION_ERROR",
            "recovery_action": "retry_with_fallback"
        },
        "tags": ["apoe", "error", "step_failure"],
        "metadata": {
            "correlation_id": execution_id,
            "plan_id": plan_id,
            "step_id": step_id
        }
    }
)
```

---

## 📋 **TIMELINE QUERY PATTERNS**

### **1. Execution History Queries**

**Query by execution_id:**
```python
# Get all timeline entries for a specific execution
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "event_types": ["apoe_plan_start", "apoe_plan_complete", "apoe_step_start", "apoe_step_complete"],
        "metadata_filter": {
            "execution_id": execution_id
        },
        "sort_by": "timestamp",
        "order": "asc"
    }
)
```

### **2. Plan History Queries**

**Query by plan_id:**
```python
# Get timeline entries for a specific plan (all executions)
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "event_types": ["apoe_plan_start", "apoe_plan_complete"],
        "metadata_filter": {
            "plan_id": plan_id
        },
        "sort_by": "timestamp",
        "order": "desc",
        "limit": 50
    }
)
```

### **3. Correlation Queries**

**Query by correlation_id:**
```python
# Get all timeline entries for a correlation ID
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "metadata_filter": {
            "correlation_id": execution_id
        },
        "sort_by": "timestamp",
        "order": "asc"
    }
)
```

### **4. Time-Range Queries**

**Query by time range:**
```python
# Get timeline entries within time range
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "event_types": ["apoe_step_complete"],
        "start_time": "2025-01-27T10:00:00Z",
        "end_time": "2025-01-27T11:00:00Z",
        "tags": ["validator"],
        "limit": 100
    }
)
```

### **5. Event Type Queries**

**Query by event type:**
```python
# Get all gate evaluations for a plan
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "event_types": ["apoe_gate_evaluation"],
        "metadata_filter": {
            "plan_id": plan_id
        }
    }
)
```

---

## 📋 **CROSS-SYSTEM INTEGRATION**

### **1. VIF Witness Linking**

**Pattern:** Include VIF witness_id in metadata

```python
# When creating timeline entry after VIF witness creation
entry = await mcp_client.call_tool(
    "mcp_lucid-mcp_add_timeline_entry",
    {
        "event_type": "apoe_step_complete",
        "title": "Step Validation Complete",
        "description": "Step validation completed successfully",
        "context_data": {...},
        "tags": ["apoe", "step_execution", "complete"],
        "metadata": {
            "correlation_id": execution_id,
            "plan_id": plan_id,
            "step_id": step_id,
            "vif_witness_id": witness_id  # Link to VIF witness
        }
    }
)

# Query timeline entries linked to VIF witness
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "metadata_filter": {
            "vif_witness_id": witness_id
        }
    }
)
```

### **2. SEG Evidence Node Linking**

**Pattern:** Include SEG evidence_id in metadata

```python
# When creating timeline entry after SEG evidence node creation
entry = await mcp_client.call_tool(
    "mcp_lucid-mcp_add_timeline_entry",
    {
        "event_type": "apoe_depp_modification",
        "title": "DEPP Modification",
        "description": "DEPP modified based on SEG evidence",
        "context_data": {
            "modification_type": "add_step",
            "evidence_source": "seg_effectiveness_patterns"
        },
        "tags": ["apoe", "depp", "modification"],
        "metadata": {
            "correlation_id": execution_id,
            "plan_id": plan_id,
            "seg_evidence_id": evidence_id  # Link to SEG evidence node
        }
    }
)

# Query timeline entries linked to SEG evidence node
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "metadata_filter": {
            "seg_evidence_id": evidence_id
        }
    }
)
```

### **3. CMC Atom Linking**

**Pattern:** Use atom_id from timeline entry creation response

```python
# Timeline entry creation automatically stores entry in CMC
result = await mcp_client.call_tool(
    "mcp_lucid-mcp_add_timeline_entry",
    {
        "event_type": "apoe_plan_start",
        ...
    }
)

# Result includes atom_id (CMC atom ID)
atom_id = result["atom_id"]  # e.g., "9868db52-1191-44a4-95d8-8ce21425796f"

# Store atom_id in APOE execution context for correlation
execution_context["timeline_atom_id"] = atom_id

# Query CMC atom from atom_id (via CMC MCP tools)
atom = await mcp_client.call_tool(
    "mcp_lucid-mcp_retrieve_memory",
    {
        "atom_id": atom_id
    }
)
```

---

## 📋 **SESSION CONTINUITY**

### **Execution State Restoration**

**Pattern:** Query timeline entries by execution_id to restore execution state

```python
async def restore_execution_state(execution_id: str) -> ExecutionState:
    """Restore execution state from timeline entries"""
    
    # Query all timeline entries for this execution
    entries = await mcp_client.call_tool(
        "mcp_lucid-mcp_get_timeline_entries",
        {
            "metadata_filter": {
                "execution_id": execution_id
            },
            "sort_by": "timestamp",
            "order": "asc"
        }
    )
    
    # Reconstruct execution state from timeline entries
    execution_state = ExecutionState()
    
    for entry in entries["entries"]:
        event_type = entry["event_type"]
        context_data = entry["context_data"]
        
        if event_type == "apoe_plan_start":
            execution_state.plan_id = context_data["plan_id"]
            execution_state.plan_name = context_data["plan_name"]
            execution_state.total_steps = context_data["total_steps"]
            execution_state.roles = context_data["roles"]
            execution_state.budget = context_data["budget"]
            execution_state.start_time = entry["timestamp"]
        
        elif event_type == "apoe_step_start":
            step_id = context_data["step_id"]
            execution_state.active_steps[step_id] = {
                "step_name": context_data["step_name"],
                "role": context_data["role"],
                "start_time": entry["timestamp"],
                "budget": context_data["budget"]
            }
        
        elif event_type == "apoe_step_complete":
            step_id = context_data["step_id"]
            if step_id in execution_state.active_steps:
                execution_state.active_steps[step_id]["status"] = context_data["status"]
                execution_state.active_steps[step_id]["confidence"] = context_data["confidence"]
                execution_state.active_steps[step_id]["outputs"] = context_data["outputs"]
                execution_state.active_steps[step_id]["duration"] = context_data["duration_seconds"]
        
        elif event_type == "apoe_plan_complete":
            execution_state.success = context_data["success"]
            execution_state.completed_steps = context_data["completed_steps"]
            execution_state.failed_steps = context_data["failed_steps"]
            execution_state.total_duration = context_data["total_duration_seconds"]
            execution_state.effectiveness_score = context_data["effectiveness_score"]
            execution_state.end_time = entry["timestamp"]
    
    return execution_state
```

---

## 📋 **IMPLEMENTATION RECOMMENDATIONS**

### **Phase 1: Basic Timeline Integration (Start Here)**

1. ✅ Integrate MCP tool `mcp_lucid-mcp_add_timeline_entry` into PlanExecutor
2. ✅ Create timeline entries for plan start/completion
3. ✅ Create timeline entries for step start/completion
4. ✅ Test timeline entry creation and retrieval

### **Phase 2: Enhanced Integration**

1. ✅ Add timeline entries for gate evaluations
2. ✅ Add timeline entries for budget milestones
3. ✅ Add timeline entries for DEPP modifications
4. ✅ Add timeline entries for errors
5. ✅ Test correlation patterns

### **Phase 3: Query Integration**

1. ✅ Implement timeline query methods in APOE
2. ✅ Add session continuity restoration via timeline
3. ✅ Add performance analysis via timeline queries
4. ✅ Test query patterns

### **Phase 4: Cross-System Integration**

1. ✅ Link timeline entries to VIF witnesses (via metadata)
2. ✅ Link timeline entries to SEG evidence nodes (via metadata)
3. ✅ Link timeline entries to CMC atoms (via atom_id from response)
4. ✅ Test cross-system correlation

---

## 📋 **PERFORMANCE CONSIDERATIONS**

### **Timeline Entry Creation**

**Performance:**
- **Latency:** ~15-30ms per entry (including CMC storage + HHNI indexing)
- **Throughput:** 100+ entries/second (typical APOE execution rates)
- **Batching:** Optional (only for >1000 events/second)

**Recommendations:**
- ✅ Use direct MCP tool calls for typical APOE rates (<100 events/second)
- ✅ Optional batching for very high-frequency events (>1000 events/second)
- ✅ Always log critical events (plan start/completion, gate evaluations, errors) immediately without batching

### **Timeline Queries**

**Performance:**
- **Simple Queries:** ~50-100ms (by execution_id, plan_id, single event type)
- **Complex Queries:** ~100-200ms (time-range + multiple event types + tags + metadata filters)
- **Large Result Sets:** ~200-500ms (1000+ entries, complex filters)

**Recommendations:**
- ✅ Use `limit` parameter to restrict result size (default: 100, max: 1000)
- ✅ Use `sort_by` and `order` for predictable ordering
- ✅ Use specific `metadata_filter` values for faster queries

---

## 📋 **INTEGRATION STATUS**

**Status:** Integration API documented, implementation recommendations provided  
**Coordination Response:** Complete (see `CHRONOS_ALEX_APOE_COORDINATION_RESPONSE.md`)  
**Integration Document:** This document (complete integration reference)

**Next Steps:**
- ⏳ @Alex: Implement Phase 1 timeline integration (plan/step events)
- ⏳ @Chronos: Update system maps with APOE integration details
- ⏳ @Both: Test timeline entry creation and retrieval

---

**Status:** Integration Documentation Complete ✅  
**Confidence:** High (0.95) - Complete API reference, implementation patterns provided  
**Next:** Wait for @Alex Phase 1 implementation feedback, update system maps

---

## 📚 **REFERENCES & BIDIRECTIONAL LINKS**

### **TCS Documentation**
- **T0 Executive:** `knowledge_architecture/systems/timeline_context_system/T0_executive.md`
- **T2 Architecture:** `knowledge_architecture/systems/timeline_context_system/T2_architecture.md`
- **T3 Detailed:** `knowledge_architecture/systems/timeline_context_system/T3_detailed.md` (APOE integration section)
- **System Map:** `knowledge_architecture/systems/timeline_context_system/system.map.lucid.json5`
- **System Index:** `knowledge_architecture/systems/timeline_context_system/system.index.lucid.json5`

### **APOE Documentation**
- **T0 Executive:** `knowledge_architecture/systems/apoe/T0_executive.md`
- **T2 Architecture:** `knowledge_architecture/systems/apoe/T2_architecture.md`
- **System Map:** `knowledge_architecture/systems/apoe/system.map.lucid.json5`

### **Connection Matrix**
- **Shared Hierarchy Mapping:** `ide_orchestration/prototypes/dac/docs/SUBSYSTEM_HIERARCHY_MAPPING.md#tcs-apoe-connection`
- **Integration Tags:** `[APOE-EXECUTION]` ↔ `[TCS-APOE]`

### **Integration Code**
- **TCS → APOE:** `packages/apoe/tcs_integration.py` - Create execution timeline entries
- **Integration Tests:** `packages/apoe/tests/test_tcs_integration.py`
- **MCP Tools:** `mcp_lucid-mcp_add_timeline_entry`, `mcp_lucid-mcp_get_timeline_entries`

---
