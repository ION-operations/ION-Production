# Chronos (TCS) - LLM API Architecture Input

**Date:** 2025-01-28  
**Route:** R-LLM-API-002  
**Status:** ✅ **INPUT COMPLETE** - TCS perspective on LLM API architecture

---

## 📋 **TCS PERSPECTIVE ON LLM API ARCHITECTURE**

**TCS Role:** Timeline logging, context building, LLM call history tracking

**Key Contributions:**
- Timeline entries for all LLM API calls
- Context retrieval for LLM calls
- LLM call history tracking
- Integration with chat/IDE orchestration

---

## 🎯 **1. PHASED APPROACH**

### **TCS Recommendation: ✅ APPROVE**

**Phase 1 (Gemini/Cerebras):**
- ✅ **Perfect timeline logging patterns** with 2 providers
- ✅ **Validate context building** with different provider characteristics
- ✅ **Test integration** with chat/IDE orchestration
- ✅ **Establish metadata standards** for LLM timeline entries

**Phase 2 (Full Expansion):**
- ✅ **Extend timeline logging** to all 6 providers
- ✅ **Provider-specific context patterns** (e.g., Gemini 1M context vs Cerebras speed)
- ✅ **Advanced context building** with multi-provider history

**Rationale:**
- Start simple, perfect patterns, then expand
- TCS timeline logging benefits from proven patterns before expansion
- Context building can be optimized per provider type

---

## 🔑 **2. MULTI-KEY STRATEGY**

### **TCS Recommendation: ✅ APPROVE with Timeline Tracking**

**Key Rotation Tracking:**
- ✅ **Timeline entries should track `key_index`** (which key was used)
- ✅ **Timeline entries should track `key_rotation_events`** (when rotation occurred)
- ✅ **Timeline entries should track `quota_exhaustion`** (when key exhausted)

**Timeline Entry Structure:**
```typescript
context_state: {
  event_type: "llm_api_call",
  provider: "gemini",
  model: "gemini-pro",
  key_index: 3,  // Which key was used (1-22)
  key_rotation_event: false,  // Was this a rotation event?
  quota_exhaustion: false,  // Did this call exhaust quota?
  // ... other LLM call data ...
}
```

**Benefits:**
- **Audit Trail:** Complete history of which keys were used
- **Debugging:** Track key rotation patterns and failures
- **Cost Analysis:** Link costs to specific keys
- **Quota Management:** Understand key exhaustion patterns

---

## 🎯 **3. STRATEGIC MODEL ROUTING**

### **TCS Recommendation: ✅ APPROVE with Context-Aware Routing**

**Timeline Context for Routing:**
- ✅ **Use timeline history** to inform provider selection
- ✅ **Track provider performance** in timeline entries
- ✅ **Link routing decisions** to timeline entries

**Context-Aware Routing Pattern:**
```typescript
// Use timeline to inform routing
const recentLLMCalls = await getTimelineEntries({
  event_type: "llm_api_call",
  limit: 10,
  filters: { provider: "gemini" }
});

// Analyze performance from timeline
const avgLatency = calculateAvgLatency(recentLLMCalls);
const successRate = calculateSuccessRate(recentLLMCalls);

// Route based on timeline context
if (avgLatency > threshold || successRate < threshold) {
  // Consider alternative provider
}
```

**Timeline Entry for Routing Decisions:**
```typescript
// Log routing decision
await addTimelineEntry({
  event_type: "llm_routing_decision",
  context_state: {
    task_type: "research",
    selected_provider: "gemini",
    routing_reason: "context_heavy_task",
    timeline_context_used: true,  // Did we use timeline for routing?
    // ... other routing data ...
  }
});
```

---

## 🔌 **4. AIM-OS INTEGRATION**

### **4.1 TCS Integration**

**Timeline Logging for LLM Calls:**
- ✅ **Every LLM API call** → Create timeline entry
- ✅ **LLM response** → Create timeline entry
- ✅ **LLM error** → Create timeline entry
- ✅ **Key rotation** → Create timeline entry
- ✅ **Provider fallback** → Create timeline entry

**Timeline Entry Structure for LLM Calls:**
```typescript
await addTimelineEntry({
  prompt_id: `llm_call_${uuid()}`,
  user_input: `LLM API Call: ${provider} ${model}`,
  context_state: {
    // Event metadata
    event_type: "llm_api_call",
    event_category: "llm_interaction",
    
    // LLM call data
    provider: "gemini",
    model: "gemini-pro",
    key_index: 3,
    endpoint: "chat-completion",
    
    // Request data
    prompt_tokens: 150,
    max_tokens: 1000,
    temperature: 0.7,
    messages_count: 5,
    
    // Response data
    response_tokens: 250,
    total_tokens: 400,
    latency_ms: 1200,
    success: true,
    
    // Context data
    chat_drawer: "coding",
    thinking_mode: "execution",
    agent_name: "Coding Agent",
    task_type: "code_generation",
    
    // Integration tags
    integration_tags: [
      "system:tcs:p0",
      "system:llm:p0",
      "integration_type:timeline",
      "connection:llm->tcs",
      "modality:tcs_timeline"
    ],
    
    // Quality metrics
    quality_metrics: {
      latency: 1200,
      token_efficiency: 0.625,  // response_tokens / total_tokens
      success: true,
    },
    
    // Technical details
    technical_details: {
      provider: "gemini",
      model: "gemini-pro",
      key_index: 3,
      api_version: "v1",
      request_id: "req_123",
    },
    
    // Metadata for query indexing
    metadata: {
      source_system: "llm_api",
      event_category: "llm_interaction",
      provider: "gemini",
      model: "gemini-pro",
      key_index: 3,
    },
    
    // External system references
    external_system_refs: {
      vif_witness_id: witnessId,  // If VIF witness created
      apoe_plan_id: planId,  // If part of APOE plan
      cas_cognitive_event_id: eventId,  // If CAS event
    },
    
    // Tags for filtering
    tags: ["llm_api", "gemini", "chat_completion", "coding", "execution"],
    
    // Current task
    current_task: `LLM API Call: ${provider} ${model} for ${task_type}`,
  }
});
```

**Context Building for LLM Calls:**
- ✅ **Retrieve timeline context** before LLM call
- ✅ **Include previous LLM interactions** in prompt context
- ✅ **Track LLM call chains** (follow-up questions, refinements)
- ✅ **Support context window management** by tracking token usage

**Context Retrieval Pattern:**
```typescript
// Before LLM call, retrieve timeline context
const timelineContext = await getTimelineEntries({
  limit: 10,
  event_type: "llm_api_call",
  filters: {
    chat_drawer: currentDrawer,
    thinking_mode: currentMode,
  }
});

// Build prompt context from timeline
const promptContext = buildPromptFromTimeline(timelineContext);

// Include in LLM call
const llmResponse = await llmClient.chat([
  ...promptContext,
  { role: "user", content: currentMessage }
]);

// Create timeline entry for LLM call
await addTimelineEntry({
  event_type: "llm_api_call",
  context_state: {
    // ... LLM call data ...
    timeline_context_used: true,
    timeline_entries_count: timelineContext.length,
    // ... other context ...
  }
});
```

**LLM Call History Tracking:**
- ✅ **Track all LLM calls** in timeline
- ✅ **Link related calls** (follow-ups, refinements)
- ✅ **Track provider/model usage patterns**
- ✅ **Support "what did we ask before?" queries**

---

### **4.2 Integration with Other Systems**

**CMC (Atlas):**
- ✅ **Timeline entries stored in CMC** with `modality="tcs_timeline"`
- ✅ **LLM call metadata** stored in CMC atoms
- ✅ **Integration tags** link LLM calls to CMC storage

**VIF (Sage):**
- ✅ **LLM calls can trigger κ-gate decisions** → Create κ-gate timeline entry
- ✅ **LLM responses can create VIF witnesses** → Link witness to timeline entry
- ✅ **Confidence tracking** for LLM responses in timeline entries

**HHNI (Sev):**
- ✅ **Timeline entries indexed in HHNI** (indirect via CMC)
- ✅ **Retrieve similar LLM interactions** from timeline history
- ✅ **Context retrieval** for LLM calls via HHNI

**SEG (Nexus):**
- ✅ **LLM responses can become evidence** → Link evidence to timeline entry
- ✅ **Evidence chains** for LLM-generated content
- ✅ **Provenance tracking** for LLM outputs

**CAS (Meta):**
- ✅ **Cognitive load tracking** for LLM calls in timeline entries
- ✅ **LLM-related drift detection** via timeline analysis
- ✅ **Cognitive context enhancement** for LLM calls

**APOE (Alex):**
- ✅ **LLM calls as part of plan execution** → Link to plan timeline entry
- ✅ **Plan step LLM calls** tracked in timeline
- ✅ **Execution timeline** includes LLM call history

---

## 🎯 **5. ARCHITECTURE DECISIONS**

### **5.1 Provider Selection Strategy**

**TCS Recommendation: Option C - Hybrid (Auto with User Override)**

**Rationale:**
- **Timeline tracking:** Need to track which provider was selected and why
- **Context building:** User preferences can inform future routing
- **Audit trail:** Complete history of provider selection decisions

**Timeline Integration:**
```typescript
// Log provider selection decision
await addTimelineEntry({
  event_type: "llm_provider_selection",
  context_state: {
    task_type: "research",
    selected_provider: "gemini",
    selection_method: "automatic",  // or "user_override"
    selection_reason: "context_heavy_task",
    user_preference: null,  // or user's preferred provider
    // ... other selection data ...
  }
});
```

---

### **5.2 Key Rotation Visibility**

**TCS Recommendation: Option C - Optional (Show in Debug/Advanced Mode)**

**Rationale:**
- **Timeline tracking:** Always track key rotation in timeline (for audit)
- **UI visibility:** Optional for users (reduce noise, show in debug mode)
- **Transparency:** Timeline provides complete audit trail

**Timeline Integration:**
```typescript
// Log key rotation event
await addTimelineEntry({
  event_type: "llm_key_rotation",
  context_state: {
    provider: "gemini",
    old_key_index: 3,
    new_key_index: 4,
    rotation_reason: "quota_exhausted",  // or "rate_limit", "error"
    visible_to_user: false,  // Hidden by default, show in debug mode
    // ... other rotation data ...
  }
});
```

---

### **5.3 Fallback Strategy**

**TCS Recommendation: Option C - Hybrid (Key Rotation, Then Provider Fallback)**

**Rationale:**
- **Timeline tracking:** Track both key rotation and provider fallback
- **Audit trail:** Complete history of fallback events
- **Debugging:** Understand fallback patterns

**Timeline Integration:**
```typescript
// Log fallback event
await addTimelineEntry({
  event_type: "llm_fallback",
  context_state: {
    fallback_type: "provider",  // or "key"
    original_provider: "gemini",
    fallback_provider: "anthropic",
    fallback_reason: "all_keys_exhausted",  // or "provider_error"
    key_rotation_attempted: true,
    keys_exhausted: 22,
    // ... other fallback data ...
  }
});
```

---

### **5.4 Cost Optimization**

**TCS Recommendation: Option B - Balance Cost/Quality/Speed**

**Rationale:**
- **Timeline tracking:** Track cost data in timeline entries
- **Context building:** Use cost history to inform routing
- **Quality preservation:** Don't sacrifice quality for cost

**Timeline Integration:**
```typescript
// Track cost in timeline entry
context_state: {
  // ... other LLM call data ...
  cost_data: {
    provider: "gemini",
    model: "gemini-pro",
    input_cost_per_1k: 0.0005,
    output_cost_per_1k: 0.0015,
    input_tokens: 150,
    output_tokens: 250,
    total_cost: 0.00045,  // Calculated cost
    cost_optimization_applied: true,
    // ... other cost data ...
  }
}
```

---

### **5.5 Response Caching**

**TCS Recommendation: Option B - Cache Only Expensive Calls (Pro Models)**

**Rationale:**
- **Timeline tracking:** Track cache hits/misses in timeline entries
- **Context building:** Cache can inform future routing
- **Cost optimization:** Cache expensive calls, fresh for cheap calls

**Timeline Integration:**
```typescript
// Track cache status in timeline entry
context_state: {
  // ... other LLM call data ...
  cache_status: {
    cached: true,  // or false
    cache_hit: true,  // or false
    cache_key: "hash_of_prompt",
    cache_age_seconds: 3600,  // If cache hit
    // ... other cache data ...
  }
}
```

---

## 📋 **6. MISSING INFRASTRUCTURE**

### **TCS Critical Needs:**

**1. Timeline Logging Hooks in LLM Client** ⚠️ **CRITICAL**
- **Need:** LLM clients must call `add_timeline_entry` after every API call
- **Priority:** P0 (MVP-Critical)
- **Timeline:** Phase 1 (Week 1)

**2. Context Retrieval Integration** ⚠️ **CRITICAL**
- **Need:** LLM clients must retrieve timeline context before API calls
- **Priority:** P0 (MVP-Critical)
- **Timeline:** Phase 1 (Week 1)

**3. LLM Call History Tracking** ✅ **READY**
- **Status:** MCP tool `add_timeline_entry` ready
- **Need:** Integration hooks in LLM clients
- **Priority:** P0 (MVP-Critical)
- **Timeline:** Phase 1 (Week 1)

**4. Provider/Model Metadata in Timeline** ✅ **READY**
- **Status:** Timeline entry structure supports provider/model metadata
- **Need:** LLM clients to populate metadata
- **Priority:** P0 (MVP-Critical)
- **Timeline:** Phase 1 (Week 1)

**5. Key Rotation Event Tracking** ✅ **READY**
- **Status:** Timeline entry structure supports key rotation events
- **Need:** APIKeyManager to create timeline entries on rotation
- **Priority:** P1 (High)
- **Timeline:** Phase 1 (Week 1)

**6. Cost Tracking in Timeline** ✅ **READY**
- **Status:** Timeline entry structure supports cost data
- **Need:** LLM clients to calculate and include cost data
- **Priority:** P1 (High)
- **Timeline:** Phase 2 (Week 2)

**7. Cache Status Tracking** ✅ **READY**
- **Status:** Timeline entry structure supports cache status
- **Need:** Caching layer to populate cache status
- **Priority:** P2 (Medium)
- **Timeline:** Phase 3 (Week 3)

---

## 🤔 **7. DISCUSSION QUESTIONS - TCS ANSWERS**

### **Q1: What timeline entries should we create for LLM calls?**

**Answer:**
- ✅ **Every LLM API call** → Create timeline entry
- ✅ **LLM response** → Create timeline entry (or combine with call entry)
- ✅ **LLM error** → Create timeline entry with error details
- ✅ **Key rotation** → Create timeline entry
- ✅ **Provider fallback** → Create timeline entry
- ✅ **Routing decision** → Create timeline entry (optional, for debugging)

**Timeline Entry Types:**
- `llm_api_call` - Main LLM API call
- `llm_response` - LLM response (can be combined with call)
- `llm_error` - LLM API error
- `llm_key_rotation` - Key rotation event
- `llm_fallback` - Provider/key fallback event
- `llm_routing_decision` - Provider selection decision (optional)

---

### **Q2: How do we link LLM interactions to user context?**

**Answer:**
- ✅ **Include chat drawer** in timeline entry (`chat_drawer: "coding" | "planning"`)
- ✅ **Include thinking mode** in timeline entry (`thinking_mode: "execution" | "research" | "synthesis"`)
- ✅ **Include agent name** in timeline entry (`agent_name: "Coding Agent"`)
- ✅ **Include task type** in timeline entry (`task_type: "code_generation" | "research" | "planning"`)
- ✅ **Link to user message** via `external_system_refs.user_message_id`
- ✅ **Link to conversation thread** via `metadata.conversation_id`

**Linking Pattern:**
```typescript
context_state: {
  // User context
  chat_drawer: "coding",
  thinking_mode: "execution",
  agent_name: "Coding Agent",
  task_type: "code_generation",
  
  // Conversation linking
  external_system_refs: {
    user_message_id: messageId,
    conversation_id: conversationId,
    thread_id: threadId,
  },
  
  // ... other context ...
}
```

---

### **Q3: Should we track LLM call history?**

**Answer: ✅ YES - CRITICAL**

**Why:**
- **Context building:** Retrieve previous LLM interactions for context
- **Follow-up questions:** Link related LLM calls (refinements, clarifications)
- **Pattern analysis:** Understand LLM usage patterns
- **Cost analysis:** Track cost trends over time
- **Quality analysis:** Track response quality over time

**Tracking Pattern:**
```typescript
// Query LLM call history
const llmHistory = await getTimelineEntries({
  event_type: "llm_api_call",
  limit: 20,
  filters: {
    chat_drawer: "coding",
    thinking_mode: "execution",
    provider: "gemini",
  }
});

// Use history for context building
const contextFromHistory = buildContextFromHistory(llmHistory);
```

---

### **Q4: How do we use timeline for LLM context building?**

**Answer:**
- ✅ **Retrieve recent LLM interactions** before new LLM call
- ✅ **Include previous prompts/responses** in context window
- ✅ **Track token usage** to manage context window limits
- ✅ **Support "what did we ask before?" queries**
- ✅ **Enable follow-up question linking**

**Context Building Pattern:**
```typescript
// Before LLM call, retrieve timeline context
async function buildLLMContext(currentMessage: string) {
  // Get recent timeline entries
  const timelineEntries = await getTimelineEntries({
    limit: 10,
    event_type: "llm_api_call",
    filters: {
      chat_drawer: currentDrawer,
      thinking_mode: currentMode,
    }
  });
  
  // Build context from timeline
  const contextMessages = timelineEntries.map(entry => ({
    role: entry.context_state.role || "assistant",
    content: entry.context_state.response_content || entry.user_input,
  }));
  
  // Add current message
  contextMessages.push({
    role: "user",
    content: currentMessage,
  });
  
  // Track token usage
  const tokenCount = estimateTokens(contextMessages);
  
  // If over limit, truncate oldest entries
  if (tokenCount > contextWindowLimit) {
    return truncateContext(contextMessages, contextWindowLimit);
  }
  
  return contextMessages;
}
```

---

## ✅ **8. ADDITIONAL CONSIDERATIONS**

### **8.1 Timeline Entry Performance**

**Concern:** Timeline entry creation adds latency to LLM calls

**Recommendation:**
- ✅ **Async timeline entry creation** (don't block LLM response)
- ✅ **Batch timeline entries** if multiple calls in quick succession
- ✅ **Optimize timeline entry structure** (minimal required fields)

---

### **8.2 Timeline Entry Storage**

**Concern:** LLM calls generate many timeline entries

**Recommendation:**
- ✅ **Store in CMC** with `modality="tcs_timeline"` (already implemented)
- ✅ **HHNI indexing** for retrieval (indirect via CMC)
- ✅ **Archive old entries** if storage becomes concern (post-MVP)

---

### **8.3 Timeline Entry Privacy**

**Concern:** Timeline entries contain sensitive LLM prompts/responses

**Recommendation:**
- ✅ **Store full content** in CMC (needed for context building)
- ✅ **Access control** via CMC permissions
- ✅ **Encryption** via CMC encryption (if implemented)

---

### **8.4 Timeline Entry Query Performance**

**Concern:** Querying timeline entries for context building adds latency

**Recommendation:**
- ✅ **Cache recent timeline entries** in memory
- ✅ **Index timeline entries** by provider/model/chat_drawer
- ✅ **Optimize query filters** (use indexed fields)

---

## 🎯 **9. TCS IMPLEMENTATION PRIORITY**

### **Phase 1 (Week 1) - MVP-Critical:**

1. ✅ **Timeline logging hooks in LLM clients** (P0)
2. ✅ **Context retrieval integration** (P0)
3. ✅ **LLM call history tracking** (P0)
4. ✅ **Provider/model metadata in timeline** (P0)

### **Phase 2 (Week 2) - High Priority:**

5. ✅ **Key rotation event tracking** (P1)
6. ✅ **Cost tracking in timeline** (P1)
7. ✅ **Advanced context building** (P1)

### **Phase 3 (Week 3) - Enhancement:**

8. ✅ **Cache status tracking** (P2)
9. ✅ **Timeline entry performance optimization** (P2)
10. ✅ **Advanced query patterns** (P2)

---

## ✅ **10. TCS READINESS SUMMARY**

**MVP Status:** ✅ **READY**

**Integration Points:**
- ✅ MCP tool `add_timeline_entry` ready
- ✅ Timeline entry structure supports LLM metadata
- ✅ Context retrieval via `get_timeline_entries` ready
- ✅ Integration patterns documented

**Implementation Needs:**
- ⚠️ LLM clients must call `add_timeline_entry` after API calls
- ⚠️ LLM clients must retrieve timeline context before API calls
- ⚠️ APIKeyManager must create timeline entries on rotation

**Support Available:**
- ✅ Help with timeline logging hooks
- ✅ Verify timeline entry creation
- ✅ Test context building patterns
- ✅ Coordinate on integration issues

---

**Status:** ✅ **INPUT COMPLETE** - TCS perspective documented, ready for team discussion  
**Confidence:** High (0.95) - Timeline logging patterns clear, integration points identified, implementation needs documented

