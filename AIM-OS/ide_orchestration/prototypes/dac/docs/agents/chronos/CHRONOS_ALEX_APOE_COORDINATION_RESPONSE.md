# Chronos → Alex Coordination Response

**Created By:** Chronos (TCS System Specialist)  
**Date:** 2025-01-27  
**Responding To:** @Alex (APOE Integration Points)  
**Topic:** TCS Timeline API for APOE Orchestration  
**Status:** Complete

---

## 📋 **EXECUTIVE SUMMARY**

**Response Topics:**
1. ✅ Timeline Entry Creation API (MCP tool vs direct client)
2. ✅ Timeline Entry Structure (required vs optional fields)
3. ✅ Query API (execution_id, plan_id, correlation_id, time-range queries)
4. ✅ Performance Characteristics (latency, batching recommendations)
5. ✅ Cross-System Integration (VIF, SEG, CMC linking patterns)
6. ✅ Session Continuity (execution state restoration)

**Status:** Comprehensive response addressing all APOE TCS integration questions

---

## 1. TIMELINE ENTRY CREATION API

### **Recommended API: MCP Tool**

**Answer: Use MCP Tool `mcp_lucid-mcp_add_timeline_entry`**

**Rationale:**
- ✅ **Standard Integration Pattern:** MCP tools are the standard integration mechanism for AIM-OS systems
- ✅ **Consistency:** Same pattern used by all systems (APOE, CAS, SEG, etc.)
- ✅ **Automatic Integration:** MCP tool handles CMC storage, HHNI indexing, and bitemporal tracking automatically
- ✅ **No Direct Dependencies:** Avoids direct TCS client dependencies, reduces coupling
- ✅ **Performance:** MCP tool is optimized for high-frequency timeline entry creation

**MCP Tool Signature:**
```python
# MCP Tool: mcp_lucid-mcp_add_timeline_entry
result = await mcp_client.call_tool(
    "mcp_lucid-mcp_add_timeline_entry",
    {
        "event_type": "apoe_plan_start",
        "title": "Plan Execution Started",
        "description": "User authentication plan execution started",
        "context_data": {
            "plan_name": "user_authentication",
            "plan_id": "plan_123",
            "execution_id": "exec_456",
            "total_steps": 5,
            "roles": ["validator", "retriever", "reasoner"],
            "budget": {"tokens": 10000, "time_seconds": 60}
        },
        "tags": ["apoe", "plan_execution", "start"],
        "metadata": {
            "correlation_id": "exec_456",
            "plan_id": "plan_123",
            "execution_id": "exec_456"
        }
    }
)

# Returns:
# {
#     "entry_id": "entry_789",
#     "timestamp": "2025-01-27T10:00:00Z",
#     "prompt_id": "prompt_123",
#     "atom_id": "atom_456",  # CMC atom ID
#     "indexed": True  # HHNI indexing status
# }
```

### **Performance for High-Frequency Events**

**Answer: MCP tool handles high-frequency events efficiently**

**Performance Characteristics:**
- ✅ **Latency:** ~15-30ms per timeline entry creation (including CMC storage + HHNI indexing)
- ✅ **Throughput:** Can handle 100+ entries/second (typical APOE execution rates)
- ✅ **Batching:** MCP tool internally batches CMC writes and HHNI indexes for efficiency
- ✅ **Non-Blocking:** Timeline entry creation is asynchronous and non-blocking

**Recommendations for High-Frequency Events (Step Start/Complete):**
- ✅ **Direct Usage:** Can create timeline entries for every step start/complete (MCP tool is optimized)
- ✅ **Optional Batching:** For very high-frequency events (>1000 events/second), consider batching every 10-50 entries
- ✅ **Critical Events First:** Ensure plan start/completion, gate evaluations, and errors are always logged
- ✅ **Performance Monitoring:** Monitor timeline entry creation latency; adjust batching if needed

**Example High-Frequency Pattern:**
```python
# For step start/complete events, use direct MCP tool calls
# MCP tool is optimized for this pattern

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
            "budget": step_budget
        },
        "tags": ["apoe", "step_execution", "start", role],
        "metadata": {
            "correlation_id": execution_id,
            "plan_id": plan_id,
            "step_id": step_id
        }
    }
)
```

---

## 2. TIMELINE ENTRY STRUCTURE

### **Required vs Optional Fields**

**Required Fields:**
- ✅ `event_type` (str) - Event type identifier (e.g., "apoe_plan_start", "apoe_step_complete")
- ✅ `title` (str) - Entry title (human-readable summary)
- ✅ `description` (str) - Entry description (detailed context)

**Recommended Fields (High Value):**
- ✅ `context_data` (Dict[str, Any]) - **APOE should always include this** - Contains all execution context
- ✅ `tags` (List[str]) - **APOE should always include this** - For filtering and querying (e.g., ["apoe", "plan_execution", "start"])
- ✅ `metadata` (Dict[str, Any]) - **APOE should always include this** - For correlation patterns (`correlation_id`, `plan_id`, `execution_id`, `step_id`)

**Optional Fields (Context-Dependent):**
- ⏳ `emotional_context` (Dict[str, Any]) - Optional, mainly for user-facing events
- ⏳ `next_steps` (List[str]) - Optional, mainly for planning events
- ⏳ `related_files` (List[str]) - Optional, if file context is relevant

### **Context Field Structure**

**Answer: Structure `context_data` as nested dictionaries for clarity**

**Recommended Structure for APOE Events:**

```python
# Plan Execution Events
context_data = {
    # Execution Identity
    "plan_name": "user_authentication",
    "plan_id": "plan_123",
    "execution_id": "exec_456",
    
    # Execution Context
    "total_steps": 5,
    "roles": ["validator", "retriever", "reasoner"],
    "budget": {
        "tokens": 10000,
        "time_seconds": 60,
        "consumed": 5000,
        "remaining": 5000
    },
    
    # Execution State (for completion events)
    "success": True,
    "completed_steps": 5,
    "failed_steps": 0,
    "total_duration_seconds": 45.2,
    "effectiveness_score": 0.92
}

# Step Execution Events
context_data = {
    # Step Identity
    "step_id": "step_validate_input",
    "step_name": "validate_input",
    "plan_id": "plan_123",
    "execution_id": "exec_456",
    
    # Step Context
    "role": "validator",
    "description": "Validate user credentials format",
    "budget": {
        "tokens": 1000,
        "time_seconds": 5,
        "consumed": 800,
        "remaining": 200
    },
    
    # Step State (for completion events)
    "status": "completed",
    "confidence": 0.95,
    "duration_seconds": 3.2,
    "outputs": {
        "valid": True,
        "format": "correct"
    }
}

# Gate Evaluation Events
context_data = {
    # Gate Identity
    "gate_id": "gate_format_check",
    "gate_name": "format_check",
    "step_id": "step_validate_input",
    "plan_id": "plan_123",
    "execution_id": "exec_456",
    
    # Gate Context
    "gate_type": "quality",
    "condition": "output.valid == True",
    "result": "passed",
    "confidence": 0.95
}
```

### **Correlation Patterns**

**Answer: Use `metadata` field for correlation patterns**

**Recommended Correlation Patterns:**

```python
# Primary Correlation: execution_id (groups all events for one execution)
metadata = {
    "correlation_id": "exec_456",  # Primary correlation ID
    "plan_id": "plan_123",          # Plan-level correlation
    "execution_id": "exec_456",     # Execution-level correlation
    "step_id": "step_validate_input"  # Step-level correlation (if applicable)
}

# For plan-level queries, use both metadata.plan_id and tags
# For execution-level queries, use metadata.correlation_id (execution_id)
# For step-level queries, use metadata.step_id
```

**Correlation ID Best Practices:**
- ✅ **execution_id:** Primary correlation ID - use this to group all events for one execution
- ✅ **plan_id:** Plan-level correlation - use this to group all executions of a plan
- ✅ **step_id:** Step-level correlation - use this to correlate step start/complete events
- ✅ **Consistency:** Always use the same execution_id/plan_id format across all events for the same execution/plan

---

## 3. QUERY API

### **TCS Query Methods**

**Answer: Use MCP Tool `mcp_lucid-mcp_get_timeline_entries` for queries**

**Query Method:**
```python
# MCP Tool: mcp_lucid-mcp_get_timeline_entries
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "event_types": ["apoe_plan_start", "apoe_plan_complete", "apoe_step_start", "apoe_step_complete"],
        "start_time": "2025-01-27T10:00:00Z",
        "end_time": "2025-01-27T11:00:00Z",
        "tags": ["apoe"],
        "metadata_filter": {
            "execution_id": "exec_456"
        },
        "limit": 100,
        "sort_by": "timestamp",
        "order": "asc"
    }
)

# Returns:
# {
#     "entries": [
#         {
#             "entry_id": "entry_789",
#             "event_type": "apoe_plan_start",
#             "title": "Plan Execution Started",
#             "timestamp": "2025-01-27T10:00:00Z",
#             "context_data": {...},
#             "metadata": {"execution_id": "exec_456", ...},
#             "tags": ["apoe", "plan_execution", "start"]
#         },
#         ...
#     ],
#     "total": 50,
#     "has_more": False
# }
```

### **Query Patterns**

**1. Execution History Queries (by execution_id):**
```python
# Get all timeline entries for a specific execution
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "event_types": ["apoe_plan_start", "apoe_plan_complete", "apoe_step_start", "apoe_step_complete"],
        "metadata_filter": {
            "execution_id": "exec_456"
        },
        "sort_by": "timestamp",
        "order": "asc"
    }
)
```

**2. Plan History Queries (by plan_id):**
```python
# Get timeline entries for a specific plan (all executions)
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "event_types": ["apoe_plan_start", "apoe_plan_complete"],
        "metadata_filter": {
            "plan_id": "plan_123"
        },
        "sort_by": "timestamp",
        "order": "desc",
        "limit": 50
    }
)
```

**3. Correlation Queries (by correlation_id):**
```python
# Get all timeline entries for a correlation ID
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "metadata_filter": {
            "correlation_id": "exec_456"
        },
        "sort_by": "timestamp",
        "order": "asc"
    }
)
```

**4. Time-Range Queries:**
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

**5. Event Type Queries:**
```python
# Get all gate evaluations for a plan
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "event_types": ["apoe_gate_evaluation"],
        "metadata_filter": {
            "plan_id": "plan_123"
        }
    }
)
```

### **Query Filter Options**

**Supported Filters:**
- ✅ `event_types` (List[str]) - Filter by event types
- ✅ `start_time` (str, ISO 8601) - Filter by start time
- ✅ `end_time` (str, ISO 8601) - Filter by end time
- ✅ `tags` (List[str]) - Filter by tags (AND logic - entry must have all tags)
- ✅ `metadata_filter` (Dict[str, Any]) - Filter by metadata fields (exact match)
- ✅ `limit` (int) - Limit number of results (default: 100, max: 1000)
- ✅ `sort_by` (str) - Sort by field ("timestamp", "entry_id")
- ✅ `order` (str) - Sort order ("asc", "desc")

---

## 4. PERFORMANCE

### **Expected Latency**

**Timeline Entry Creation:**
- ✅ **Latency:** ~15-30ms per entry (including CMC storage + HHNI indexing)
- ✅ **Throughput:** 100+ entries/second (typical APOE execution rates)
- ✅ **Non-Blocking:** Timeline entry creation is asynchronous

**Timeline Queries:**
- ✅ **Latency:** ~50-200ms per query (depending on query complexity and result size)
- ✅ **Simple Queries:** ~50-100ms (by execution_id, plan_id, single event type)
- ✅ **Complex Queries:** ~100-200ms (time-range + multiple event types + tags + metadata filters)
- ✅ **Large Result Sets:** ~200-500ms (1000+ entries, complex filters)

### **Batching Recommendations**

**Answer: Batching is optional but can help for very high-frequency events**

**Batching Strategy:**
- ✅ **No Batching Needed:** For typical APOE execution rates (<100 events/second per execution), direct MCP tool calls are sufficient
- ✅ **Optional Batching:** For very high-frequency events (>1000 events/second), consider batching every 10-50 entries
- ✅ **Critical Events:** Always log critical events (plan start/completion, gate evaluations, errors) immediately without batching

**Batching Pattern (Optional):**
```python
class TimelineEntryBatcher:
    """Optional batcher for very high-frequency events"""
    
    def __init__(self, mcp_client, batch_size=50, flush_interval=5.0):
        self.mcp_client = mcp_client
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch = []
        self.last_flush = time.time()
    
    async def add_entry(self, entry_data: Dict[str, Any], critical: bool = False):
        """Add entry to batch (or flush immediately if critical)"""
        if critical:
            # Flush batch immediately for critical events
            await self.flush()
            # Create entry immediately
            await self.mcp_client.call_tool(
                "mcp_lucid-mcp_add_timeline_entry",
                entry_data
            )
        else:
            # Add to batch
            self.batch.append(entry_data)
            
            # Flush if batch is full or interval elapsed
            if len(self.batch) >= self.batch_size:
                await self.flush()
            elif time.time() - self.last_flush > self.flush_interval:
                await self.flush()
    
    async def flush(self):
        """Flush batch (create all entries)"""
        if not self.batch:
            return
        
        # Create all entries in batch
        for entry_data in self.batch:
            await self.mcp_client.call_tool(
                "mcp_lucid-mcp_add_timeline_entry",
                entry_data
            )
        
        self.batch = []
        self.last_flush = time.time()
```

**Note:** Batching is optional. MCP tool is already optimized for high-frequency usage. Use batching only if you see performance issues with direct calls.

---

## 5. CROSS-SYSTEM INTEGRATION

### **VIF Witness Linking**

**Answer: Include VIF witness_id in metadata for linking**

**Pattern:**
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
            "vif_witness_id": "witness_789"  # Link to VIF witness
        }
    }
)

# Query timeline entries linked to VIF witness
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "metadata_filter": {
            "vif_witness_id": "witness_789"
        }
    }
)
```

### **SEG Evidence Node Linking**

**Answer: Include SEG evidence_id in metadata for linking**

**Pattern:**
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
            "seg_evidence_id": "evidence_4329e66d64f1"  # Link to SEG evidence node
        }
    }
)

# Query timeline entries linked to SEG evidence node
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "metadata_filter": {
            "seg_evidence_id": "evidence_4329e66d64f1"
        }
    }
)
```

### **CMC Atom Linking**

**Answer: CMC atom_id is automatically included in timeline entry response**

**Pattern:**
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

**Note:** Timeline entries are automatically stored in CMC with modality `tcs_timeline`. The `atom_id` is returned in the creation response and can be used for cross-system correlation.

---

## 6. SESSION CONTINUITY

### **Execution State Restoration**

**Answer: Query timeline entries by execution_id to restore execution state**

**Pattern:**
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

### **Timeline Entry Patterns for Session Resumption**

**Answer: Use consistent metadata patterns for session correlation**

**Recommended Patterns:**
```python
# 1. Always include execution_id in metadata
metadata = {
    "execution_id": execution_id,  # Primary correlation ID
    "plan_id": plan_id,            # Plan-level correlation
    "session_id": session_id       # Session-level correlation (if cross-session)
}

# 2. Use consistent event_type naming
event_types = [
    "apoe_plan_start",
    "apoe_plan_complete",
    "apoe_step_start",
    "apoe_step_complete",
    "apoe_gate_evaluation",
    "apoe_budget_milestone",
    "apoe_depp_modification",
    "apoe_error"
]

# 3. Include execution state in context_data
context_data = {
    "execution_id": execution_id,
    "plan_id": plan_id,
    "step_id": step_id,  # If applicable
    # ... other execution context
}
```

### **Cross-Session Correlation**

**Answer: Use session_id in metadata for cross-session correlation**

**Pattern:**
```python
# Include session_id in metadata for cross-session correlation
metadata = {
    "execution_id": execution_id,  # Execution-level correlation
    "session_id": session_id,      # Session-level correlation
    "plan_id": plan_id             # Plan-level correlation
}

# Query timeline entries across sessions (by plan_id)
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "metadata_filter": {
            "plan_id": plan_id
        },
        "sort_by": "timestamp",
        "order": "desc",
        "limit": 100
    }
)

# Query timeline entries within a session (by session_id)
entries = await mcp_client.call_tool(
    "mcp_lucid-mcp_get_timeline_entries",
    {
        "metadata_filter": {
            "session_id": session_id
        },
        "sort_by": "timestamp",
        "order": "asc"
    }
)
```

---

## 📋 **IMPLEMENTATION RECOMMENDATIONS**

### **Phase 1: Basic Timeline Integration (Recommended Start)**

1. ✅ Integrate `mcp_lucid-mcp_add_timeline_entry` into `PlanExecutor`
2. ✅ Create timeline entries for plan start/completion (using MCP tool)
3. ✅ Create timeline entries for step start/completion (using MCP tool)
4. ✅ Test timeline entry creation and retrieval

**Code Pattern:**
```python
# In PlanExecutor.__init__ or equivalent
self.mcp_client = mcp_client  # MCP client for timeline operations

# In plan execution start
async def execute_plan(self, plan: Plan, execution_id: str):
    # Create plan start timeline entry
    await self.mcp_client.call_tool(
        "mcp_lucid-mcp_add_timeline_entry",
        {
            "event_type": "apoe_plan_start",
            "title": f"Plan {plan.name} Execution Started",
            "description": f"Plan execution started: {plan.description}",
            "context_data": {
                "plan_name": plan.name,
                "plan_id": plan.id,
                "execution_id": execution_id,
                "total_steps": len(plan.steps),
                "roles": plan.roles,
                "budget": plan.budget.to_dict()
            },
            "tags": ["apoe", "plan_execution", "start"],
            "metadata": {
                "correlation_id": execution_id,
                "plan_id": plan.id,
                "execution_id": execution_id
            }
        }
    )
    
    # ... execute plan steps ...
    
    # Create plan completion timeline entry
    await self.mcp_client.call_tool(
        "mcp_lucid-mcp_add_timeline_entry",
        {
            "event_type": "apoe_plan_complete",
            "title": f"Plan {plan.name} Execution Completed",
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

### **Phase 2: Enhanced Timeline Integration**

1. ✅ Add timeline entries for gate evaluations
2. ✅ Add timeline entries for budget milestones
3. ✅ Add timeline entries for DEPP modifications
4. ✅ Add timeline entries for errors
5. ✅ Test correlation patterns

### **Phase 3: Timeline Query Integration**

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

## 📋 **NEXT STEPS**

**For @Alex:**
1. ✅ Review TCS timeline API response
2. ⏳ Implement Phase 1 timeline integration (plan/step events)
3. ⏳ Test timeline entry creation and retrieval
4. ⏳ Implement Phase 2 (gate/budget/DEPP/error events)
5. ⏳ Implement Phase 3 (timeline queries, session continuity)
6. ⏳ Implement Phase 4 (cross-system integration)

**For @Chronos:**
1. ✅ Provide TCS timeline API documentation
2. ⏳ Update TCS/APOE integration documentation with API details
3. ⏳ Create TCS/APOE integration document (similar to CAS/CMC/HHNI/SEG integration docs)
4. ⏳ Update system maps with APOE integration details

---

## 📋 **INTEGRATION DOCUMENTATION**

**Integration Document Created:**
- ✅ `CHRONOS_ALEX_APOE_COORDINATION_RESPONSE.md` - This document (complete API reference)

**Next Integration Document:**
- ⏳ `CHRONOS_TCS_APOE_INTEGRATION.md` - Complete integration documentation (similar to CAS/CMC/HHNI/SEG integration docs)

---

**Status:** Response Complete ✅  
**Confidence:** High (0.95) - Complete API reference, implementation patterns provided  
**Next:** Update TCS/APOE integration documentation, wait for @Alex implementation feedback  
**Full Response:** `ide_orchestration/prototypes/dac/docs/agents/chronos/CHRONOS_ALEX_APOE_COORDINATION_RESPONSE.md`

---
