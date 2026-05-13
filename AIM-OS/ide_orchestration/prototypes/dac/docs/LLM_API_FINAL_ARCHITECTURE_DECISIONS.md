# LLM API Architecture - Final Decisions

**Created:** 2025-01-28  
**Status:** ✅ **FINALIZED** - All team input synthesized  
**Route:** R-LLM-API-002  
**Priority:** P0 - Critical for chat/IDE MVP

---

## 🎯 **EXECUTIVE SUMMARY**

After comprehensive team discussion (9/9 agents responded), we have finalized the LLM API architecture for AIM-OS chat/IDE system. This document captures all final decisions, implementation priorities, and next steps.

**Key Outcomes:**
- ✅ Phased approach: Phase 1 (Gemini/Cerebras MVP), Phase 2 (Full expansion)
- ✅ Multi-key strategy: 22 keys per provider (132 total keys)
- ✅ Strategic routing: Provider selection based on task type
- ✅ AIM-OS integration: All systems integrated (CMC, VIF, HHNI, SEG, CAS, TCS, APOE, SDF-CVF)
- ✅ Team consensus on all 5 key decisions

---

## 📋 **FINAL ARCHITECTURE DECISIONS**

### **1. Provider Selection Strategy**

**Decision:** ✅ **Option C (Hybrid)** - Automatic routing with user override capability

**Rationale:**
- 6/8 agents voted for hybrid approach
- Automatic routing for efficiency (orchestrator knows best)
- User override for power users and debugging
- Best of both worlds

**Implementation:**
- Orchestrator automatically selects provider based on task type
- UI provides override option in advanced/debug mode
- Override persists for session or can be saved per-user

**Strategic Routing Matrix:**
- **Speed-Critical:** Cerebras / DeepInfra (Orchestrator, ConciseReplyAgent)
- **Context-Heavy:** Gemini / Anthropic (DeepResearchAgent, APOEAgent, SDFAgent)
- **Reasoning-Heavy:** Gemini Pro / Anthropic Opus / OpenAI GPT-4 (RelationAgent, DocAgent, VerifierAgent)
- **Function Calling:** OpenAI / Anthropic (FunctionCallingAgent)
- **Industry Standard:** OpenAI (compatibility requirements)
- **Open Source:** Replicate / DeepInfra (custom models, flexibility)

---

### **2. Key Rotation Visibility**

**Decision:** ✅ **Option C (Optional)** - Show in debug/advanced mode only

**Rationale:**
- 5/8 agents voted for optional visibility
- Most users don't need to see key rotation
- Power users/debuggers can enable visibility
- Reduces UI clutter

**Implementation:**
- Key rotation happens automatically (transparent to users)
- Debug/advanced mode shows: current key index, rotation events, quota status
- Optional UI indicator for key health (green/yellow/red)

---

### **3. Fallback Strategy**

**Decision:** ✅ **Option C (Hybrid)** - Key rotation first, then provider fallback

**Rationale:**
- 6/8 agents voted for hybrid fallback
- Exhaust all keys within provider before switching
- Provider fallback as last resort
- Maximizes quota utilization

**Implementation:**
1. Try current key for provider
2. If quota/rate limit → Rotate to next key (up to 22 keys)
3. If all keys exhausted → Try fallback provider (if configured)
4. If all providers exhausted → Error with helpful message

**Fallback Chain Example:**
```
1. Try Gemini Pro (Key 1)
2. If quota exhausted → Try Gemini Pro (Key 2-22)
3. If all Gemini keys exhausted → Try Anthropic Claude
4. If Anthropic exhausted → Try OpenAI GPT-4
5. If all exhausted → Error
```

---

### **4. Cost Optimization**

**Decision:** ✅ **Option B (Balance)** - Balance cost/quality/speed

**Rationale:**
- 7/8 agents voted for balanced approach
- Quality and speed matter as much as cost
- Automatic optimization based on task type
- User can override if needed (via Decision 1)

**Implementation:**
- Task-based routing (speed vs quality vs cost)
- Cost tracking per key/provider (stored in CMC)
- Cost optimization queries (Atlas recommendations)
- User-configurable cost preferences (optional)

---

### **5. Response Caching**

**Decision:** ✅ **Option B (Cache expensive only)** - Cache Pro models, not Flash/fast models

**Rationale:**
- 5/8 agents voted for cache expensive only
- Pro models are expensive (Gemini Pro, Claude Opus, GPT-4)
- Flash/fast models are cheap (no need to cache)
- Balance between cost savings and freshness

**Implementation:**
- Cache responses from: Gemini Pro, Claude Opus, GPT-4
- Don't cache: Gemini Flash, Claude Haiku, Cerebras, DeepInfra
- Cache key: provider + model + prompt hash
- Cache TTL: Configurable (default: 1 hour)

---

## 🏗️ **ARCHITECTURE DESIGN**

### **End-to-End Flow**

```
User Message (UI)
  ↓
AdvancedChatPanel (captures: transcript, thinking mode, toggles, IntegrationTagContext)
  ↓
AdvancedLLMService (layers: thinking-mode presets, deep-search, AIM-OS hooks)
  ↓
LLMService (transforms to MCP payload, calls Command Server)
  ↓
Command Server: POST /mcp/execute
  {
    tool: "call_api",
    arguments: {
      provider: "gemini" | "cerebras" | ...,
      endpoint: "chat-completion",
      data: { model, messages, temperature, ... },
      integrate_aimos: true
    }
  }
  ↓
MCP Server: call_api()
  ↓
APIServiceRegistry.call_api()
  ↓
APIKeyManager.get_key() → Rotate if needed
  ↓
GeminiClient / CerebrasClient / etc.
  ↓
Actual LLM API Call (Gemini SDK / Cerebras REST / etc.)
  ↓
Response Processing
  ↓
AIM-OS Integration (CMC atom + VIF witness immediately)
  ↓
Response to UI
  ↓
AIMOSIntegrationService (stores atom, indexes in HHNI, creates witness, synthesizes SEG)
```

### **Context Capture & Persistence**

**UI-Generated Integration Tags:**
- Every MCP call tagged with: system, integrationType, connection, modality, action, mode, agent, extras
- Tags trace every call to originating chat action
- Consistent provenance across all systems

**AIMOSIntegrationService Creates:**
1. **CMC Atom:** Full request/response, metadata (provider, model, key_index, tokens, cost, latency)
2. **HHNI Index:** Semantic search entry, provider/model filtering, temporal indexing
3. **VIF Witness:** Mandatory witness with provider-specific confidence baseline, κ-gating
4. **SEG Synthesis:** Evidence nodes, graph linking, provenance tracking
5. **TCS Timeline:** Timeline entry with provider/model/key/tokens/latency
6. **CAS Cognitive:** Cognitive load tracking, usage patterns, context streaming
7. **SDF-CVF Quality:** Quartet/parity validation, evidence linking
8. **APOE Plan:** Plan execution tracking, LLM-based steps

**Context Retrieval:**
- **HHNI:** Semantic similarity search (provider-aware)
- **TCS:** Chronological context (session history, timeline entries)
- **SEG:** Evidence graph nodes (provenance, relationships)
- **VIF:** Confidence baselines (provider-specific)
- **CAS:** Cognitive context (attention metrics, cold principles)

---

## 🔌 **AIM-OS INTEGRATION SPECIFICATIONS**

### **Atlas (CMC) - Storage & Tags**

**Storage Pattern:**
```python
AtomCreate(
    modality="llm_api_call",
    content=AtomContent(
        inline=json.dumps({
            "request": { "provider": "gemini", "model": "gemini-2.5-pro", ... },
            "response": { "content": "...", "tokens": 150, ... }
        }),
        media_type="application/json"
    ),
    tags={
        "llm": 1.0,
        "api_call": 1.0,
        "provider:gemini": 1.0,
        "model:gemini-2.5-pro": 1.0,
        "key_index:1": 1.0,
        "task_type:research": 1.0,
        "agent:deep_research": 1.0,
        "mode:research": 1.0
    },
    metadata={
        "provider": "gemini",
        "model": "gemini-2.5-pro",
        "key_index": 1,
        "tokens": 150,
        "cost": 0.0015,
        "latency_ms": 1250,
        "task_type": "research",
        "agent": "deep_research",
        "thinking_mode": "research",
        "timestamp": "2025-01-28T14:30:00Z"
    }
)
```

**Cost Tracking:**
- Store cost per key/provider in CMC metadata
- Aggregate costs in CMC queries
- Support cost optimization queries

---

### **Sage (VIF) - Confidence & Witnesses**

**Confidence Baselines:**
- **Gemini Pro / Claude Opus / GPT-4:** 0.85-0.95 (high)
- **Gemini Flash / Claude Haiku:** 0.75-0.85 (medium)
- **Cerebras / DeepInfra:** 0.70-0.80 (lower)

**Witness Creation:**
```python
VIFWitness(
    context_snapshot_id="snapshot_xyz",
    confidence=0.90,  # Provider-specific baseline
    provider="gemini",
    model="gemini-2.5-pro",
    key_index=1,
    tokens=150,
    cost=0.0015,
    latency_ms=1250,
    task_type="research",
    agent="deep_research",
    kappa_gate_passed=True,
    task_criticality="high"
)
```

**κ-Gating:**
- **Critical tasks:** κ ≥ 0.90 (use Pro models)
- **Routine tasks:** κ ≥ 0.70 (use Flash/fast models)
- Provider confidence baseline affects κ-gate thresholds

---

### **Sev (HHNI) - Indexing & Retrieval**

**Indexing:**
- Index all LLM responses in HHNI (full semantic search)
- Handle context window limits: Index summaries for large responses
- Support provider/model filtering
- Support temporal indexing

**Retrieval:**
- Retrieve relevant context for LLM calls (past interactions, similar queries)
- Provider-specific retrieval (e.g., "similar Gemini Pro responses")
- Temporal retrieval (recent responses, historical patterns)
- Context-aware retrieval (user context, session context)

---

### **Nova (SDF-CVF) - Quality & Evidence**

**Quality Validation:**
- Validate LLM response quality using quartet/parity checks
- Track parity for LLM outputs (code, documentation, reasoning)
- Handle LLM-generated code with quartet validation
- Quality gates based on parity thresholds

**Evidence Linking:**
- Link LLM responses to SEG evidence chains
- Create evidence nodes for LLM calls
- Track LLM response provenance
- Support evidence-based quality validation

---

### **Meta (CAS) - Cognitive Monitoring**

**Cognitive Load:**
- Track cognitive load for LLM calls (context size, complexity)
- Monitor LLM usage patterns (which providers/models used most)
- Detect LLM-related cognitive drift
- Alert on excessive LLM usage

**Context Enhancement:**
- Stream cognitive context to LLM calls (attention metrics, cold principles)
- Cognitive state affects provider selection (high load → use fast models)
- Enhance LLM prompts with cognitive context
- Support cognitive-aware routing

---

### **Chronos (TCS) - Timeline Logging**

**Timeline Entries:**
```python
TimelineEntry(
    prompt_id="prompt_xyz",
    timestamp="2025-01-28T14:30:00Z",
    context_state={
        "provider": "gemini",
        "model": "gemini-2.5-pro",
        "key_index": 1,
        "tokens": 150,
        "cost": 0.0015,
        "latency_ms": 1250,
        "task_type": "research",
        "agent": "deep_research"
    },
    timeline_entry={
        "type": "llm_api_call",
        "provider": "gemini",
        "model": "gemini-2.5-pro",
        "tokens": 150,
        "cost": 0.0015
    }
)
```

**Context Retrieval:**
- Retrieve timeline context for LLM calls (past interactions, user history)
- Timeline entries include provider/model info
- Use timeline for LLM context building
- Support temporal queries (recent LLM calls, historical patterns)

---

### **Nexus (SEG) - Evidence Graphs**

**Evidence Nodes:**
- Create evidence nodes for LLM calls
- Link LLM responses to evidence chains
- Track LLM response provenance
- Support evidence-based quality validation

**Graph Integration:**
- Link LLM calls to SEG graph (entities, relations, evidence)
- Track LLM-generated content in evidence graphs
- Support graph-based retrieval for LLM context
- Evidence graphs enhance LLM context

---

### **Alex (APOE) - Plan Execution**

**Plan Integration:**
- LLM calls can be part of APOE plan executions
- Track LLM calls in plan execution metadata
- Support LLM-based plan steps
- Link LLM responses to plan outcomes

**Execution Tracking:**
- Store LLM calls in plan execution atoms
- Include LLM calls in plan statistics (tokens, cost, latency)
- Support LLM-based plan recommendations
- Track LLM usage in plan history

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: MVP (Week 1) - Critical**

**Day 1-2: Core Infrastructure**
1. ✅ Create `api_service_registry` module
2. ✅ Implement `LLMClient` abstract base class
3. ✅ Implement `APIKeyManager` (22-key support, rotation, usage tracking)
4. ✅ Implement `APIServiceRegistry` (dual interface: clients + MCP tool)

**Day 3-4: Provider Clients**
1. ✅ Implement `GeminiClient` (using `google-generativeai` SDK)
2. ✅ Implement `CerebrasClient` (using REST API)
3. ✅ Test with real API keys
4. ✅ Implement key rotation logic

**Day 5: MCP Integration**
1. ✅ Wire `api_service_registry` into `lucid_mcp_server.call_api`
2. ✅ Test end-to-end flow (UI → Command Server → MCP → API)
3. ✅ Verify AIM-OS integration hooks fire

**Day 6-7: AIM-OS Integration (Phase 1)**
1. ✅ Basic CMC storage (Atlas recommendations)
2. ✅ Basic VIF witness creation (Sage recommendations)
3. ✅ Basic timeline logging (Chronos recommendations)
4. ✅ Test full integration flow

---

### **Phase 2: Full Integration (Week 2)**

**Day 8-10: Complete AIM-OS Integration**
1. ✅ Full CMC integration (tags, cost tracking)
2. ✅ Full VIF integration (confidence baselines, κ-gating)
3. ✅ Full HHNI integration (indexing, retrieval)
4. ✅ Full TCS integration (timeline entries, context retrieval)
5. ✅ Full SEG integration (evidence nodes, graph linking)
6. ✅ Full CAS integration (cognitive monitoring, context streaming)
7. ✅ Full SDF-CVF integration (quality validation, evidence linking)
8. ✅ Full APOE integration (plan execution tracking)

**Day 11-12: Orchestrator Routing**
1. ✅ Implement orchestrator-side routing (hybrid default + override UI)
2. ✅ Task type detection
3. ✅ Automatic client injection
4. ✅ User override UI (advanced/debug mode)

**Day 13-14: Testing & Validation**
1. ✅ End-to-end testing (all providers, all integrations)
2. ✅ Performance testing (latency, throughput)
3. ✅ Cost tracking validation
4. ✅ Key rotation validation

---

### **Phase 3: Expansion (Week 3)**

**Day 15-17: Additional Providers**
1. ✅ Implement `AnthropicClient`
2. ✅ Implement `OpenAIClient`
3. ✅ Implement `DeepInfraClient`
4. ✅ Implement `ReplicateClient`
5. ✅ Test all providers

**Day 18-19: Advanced Features**
1. ✅ Response caching (expensive models only)
2. ✅ Cost tracking dashboard
3. ✅ Quota monitoring dashboard
4. ✅ Key health monitoring

**Day 20-21: Optimization**
1. ✅ Advanced provider selection
2. ✅ Fallback chain optimization
3. ✅ Load balancing
4. ✅ Performance optimization

---

## 📋 **MISSING INFRASTRUCTURE CHECKLIST**

### **Critical (Phase 1):**
- [ ] `api_service_registry` module (doesn't exist)
- [ ] `LLMClient` abstract base class
- [ ] `GeminiClient` implementation
- [ ] `CerebrasClient` implementation
- [ ] `APIKeyManager` (22-key support)
- [ ] Key rotation logic
- [ ] Usage tracking
- [ ] MCP Server integration
- [ ] Basic CMC storage integration
- [ ] Basic VIF witness creation
- [ ] Basic timeline logging

### **Important (Phase 2):**
- [ ] Full AIM-OS integration (all systems)
- [ ] Orchestrator model routing
- [ ] Agent registry with LLM preferences
- [ ] Task type detection
- [ ] Automatic client injection
- [ ] User override UI

### **Enhancement (Phase 3):**
- [ ] `AnthropicClient` implementation
- [ ] `OpenAIClient` implementation
- [ ] `DeepInfraClient` implementation
- [ ] `ReplicateClient` implementation
- [ ] Response caching
- [ ] Cost tracking dashboard
- [ ] Quota monitoring dashboard
- [ ] Key health monitoring

---

## 🎯 **SUCCESS CRITERIA**

### **Phase 1 MVP:**
- ✅ `api_service_registry` module exists and works
- ✅ Gemini + Cerebras clients functional
- ✅ 22-key rotation working
- ✅ MCP Server integration complete
- ✅ Basic AIM-OS integration (CMC, VIF, TCS)
- ✅ End-to-end flow tested (UI → API → AIM-OS)

### **Phase 2 Full Integration:**
- ✅ All AIM-OS systems integrated
- ✅ Orchestrator routing functional
- ✅ User override UI working
- ✅ All integrations tested

### **Phase 3 Expansion:**
- ✅ All 6 providers functional
- ✅ Advanced features working
- ✅ Performance optimized
- ✅ Production-ready

---

## 📚 **KEY REFERENCES**

1. **Team Discussion:** `LLM_API_TEAM_DISCUSSION.md`
2. **Team Responses:** `LLM_API_TEAM_RESPONSES_SUMMARY.md`
3. **Implementation Plan:** `LLM_API_IMPLEMENTATION_PLAN_GEMINI_CEREBRAS.md`
4. **Strategic Routing:** `LLM_STRATEGIC_MODEL_ROUTING.md`
5. **Expansion Roadmap:** `LLM_PROVIDER_EXPANSION_ROADMAP.md`

---

**Status:** ✅ **FINALIZED** - Ready for implementation  
**Next:** Begin Phase 1 implementation (api_service_registry module)

