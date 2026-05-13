# LLM API Architecture - Team Discussion

**Created:** 2025-01-28  
**Status:** 🟡 **OPEN FOR TEAM DISCUSSION**  
**Priority:** P0 - Critical for chat/IDE MVP  
**Route:** R-LLM-API-002

---

## 🎯 **PURPOSE**

Discuss and align on the complete LLM API architecture for AIM-OS chat/IDE system, including:
1. Phased implementation approach (Phase 1: Gemini/Cerebras, Phase 2: Full expansion)
2. Multi-key strategy (22 keys per provider, 132 total keys)
3. Strategic model routing (which provider for which task/agent)
4. Integration with chat/IDE orchestration
5. Missing infrastructure needs

**This builds on the team-wide LLM API discussion (R-LLM-API-001) and the Aether↔Codex architecture discussion (R-CODEX-ARCH-001).**

---

## 📋 **CURRENT STATUS**

### ✅ **What's Working:**
- UI → Command Server → MCP Server flow is complete
- `LLMService.chatCompletion()` calls `/mcp/execute` with `call_api` tool
- MCP server has `call_api()` function ready

### ❌ **What's Missing:**
- `api_service_registry` module doesn't exist
- No actual LLM API calls are happening
- No provider-specific handling
- No key rotation logic
- No strategic routing

### 📄 **Reference Documents:**
- **Implementation Plan:** `LLM_API_IMPLEMENTATION_PLAN_GEMINI_CEREBRAS.md` ⭐
- **Strategic Routing:** `LLM_STRATEGIC_MODEL_ROUTING.md` ⭐
- **Expansion Roadmap:** `LLM_PROVIDER_EXPANSION_ROADMAP.md` ⭐
- **Architecture Discussion:** `AETHER_CODEX_CHAT_IDE_ARCHITECTURE_DISCUSSION.md`
- **LLM API Status:** `LLM_API_CONNECTION_STATUS.md`
- **Team LLM Discussion:** `LLM_API_ARCHITECTURE_DISCUSSION.md` (R-LLM-API-001)

---

## 🎯 **PHASED APPROACH**

### **Phase 1: MVP - Perfect the System (2-3 days)**
- ✅ **Gemini API** (using `google-generativeai` SDK)
- ✅ **Cerebras API** (using REST API)
- **Goal:** Perfect the architecture, key rotation, and integration patterns
- **Keys:** 44 total (22 Gemini + 22 Cerebras)

### **Phase 2: Full Expansion (3-5 days)**
- ✅ **Anthropic API** (Claude - REST API)
- ✅ **OpenAI API** (GPT-4, GPT-3.5 - REST API)
- ✅ **DeepInfra API** (Various models - REST API)
- ✅ **Replicate API** (Open source models - REST API)
- **Goal:** Complete provider ecosystem
- **Keys:** 132 total (22 × 6 providers)

**Rationale:**
- Start with Gemini + Cerebras to perfect the system
- Then expand using the same proven patterns
- Each provider has strategic strengths

---

## 🔑 **MULTI-KEY STRATEGY (22 KEYS PER PROVIDER)**

### **Why 22 Keys?**
- Overcome free tier limits (e.g., Gemini: 50 Pro RPD × 22 = 1,100 RPD)
- Automatic rotation when quota/rate limits hit
- Massive combined capacity across all providers
- Resilient to individual key/account failures

### **Key Rotation Logic:**
1. Pick current key for provider
2. Make API call
3. If 429/quota error → Mark key exhausted, rotate to next
4. Retry with next key (up to 22 keys)
5. If all exhausted → Try fallback provider (if configured)

### **Usage Tracking:**
- Track per key: requests, tokens, errors, last_used
- Monitor quota exhaustion status
- Monitor rate limit status
- Support health monitoring dashboard

---

## 🎯 **STRATEGIC MODEL ROUTING**

### **Speed-Critical Tasks → Cerebras / DeepInfra**
- **Agents:** Orchestrator, ConciseReplyAgent
- **Use Cases:** Task classification, simple chat, tool formatting
- **Rationale:** Need response in milliseconds, not seconds

### **Context-Heavy Tasks → Gemini / Anthropic**
- **Agents:** DeepResearchAgent, APOEAgent, SDFAgent
- **Use Cases:** Research with large documents, planning with multiple files
- **Rationale:** Only Gemini (1M) or Anthropic (200K) can handle this

### **Reasoning-Heavy Tasks → Gemini Pro / Anthropic Opus / OpenAI GPT-4**
- **Agents:** RelationAgent, DocAgent, VerifierAgent
- **Use Cases:** Complex synthesis, reasoning, validation
- **Rationale:** High-level reasoning requires powerful models

### **Function Calling Tasks → OpenAI / Anthropic**
- **Agents:** FunctionCallingAgent
- **Use Cases:** Tool use, structured outputs, API integrations
- **Rationale:** Best function calling support

### **Industry Standard → OpenAI**
- **Use Cases:** Compatibility requirements, ecosystem integration
- **Rationale:** Widest compatibility

### **Open Source / Custom → Replicate / DeepInfra**
- **Use Cases:** Custom models, self-hosted options, flexibility
- **Rationale:** Open source access, custom deployments

---

## 🏗️ **ARCHITECTURE DESIGN**

### **LLMClient Abstraction Pattern**

```python
class LLMClient(ABC):
    """Abstract base class for all LLM API clients."""
    
    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generates a simple text completion."""
        pass
    
    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> dict:
        """Generates a chat-based completion."""
        pass
```

**Benefits:**
- Agents don't know/care about provider details
- Easy to swap providers
- Consistent interface across all providers
- Supports strategic routing

### **APIKeyManager (22-Key Support)**

```python
class APIKeyManager:
    """Manages multiple API keys per provider with rotation"""
    
    def get_key(self, provider: str) -> Optional[str]:
        """Get current key, auto-rotate if exhausted"""
        pass
    
    def rotate_key(self, provider: str) -> Optional[str]:
        """Rotate to next available key"""
        pass
    
    def record_usage(self, key: str, tokens: int, error: bool):
        """Track usage per key"""
        pass
```

**Features:**
- Supports up to 22 keys per provider
- Automatic rotation on quota/rate limit
- Usage tracking per key
- Health monitoring

### **APIServiceRegistry (Dual Interface)**

```python
class APIServiceRegistry:
    """Registry for LLM clients and MCP tool integration"""
    
    def get_client(self, provider: str) -> LLMClient:
        """Get LLMClient for agent use"""
        pass
    
    def call_api(self, provider: str, endpoint: str, ...) -> dict:
        """MCP tool interface for chat/IDE"""
        pass
```

**Dual Purpose:**
- **For Agents:** `get_client()` returns LLMClient instance
- **For MCP Tools:** `call_api()` provides standardized interface

---

## 🔌 **CHAT/IDE INTEGRATION**

### **How LLM Calls Integrate with Chat/IDE:**

```
User Message
  ↓
Chat UI (AdvancedChatPanel)
  ↓
LLMService.chatCompletion()
  ↓
Command Server: POST /mcp/execute
  {
    tool: "call_api",
    arguments: {
      provider: "gemini" | "cerebras" | ...,
      endpoint: "chat-completion",
      data: { model, messages, temperature, ... }
    }
  }
  ↓
MCP Server: call_api()
  ↓
APIServiceRegistry.call_api()
  ↓
GeminiClient / CerebrasClient / etc.
  ↓
APIKeyManager.get_key() → Rotate if needed
  ↓
Actual LLM API Call (Gemini SDK / Cerebras REST / etc.)
  ↓
Response Processing
  ↓
AIM-OS Integration (CMC, VIF, TCS, SEG, CAS)
  ↓
Response to UI
```

### **Orchestrator Model Routing:**

```python
class Orchestrator:
    def route_to_agent(self, task_type: str, agent: Agent):
        """Route appropriate LLM client to agent"""
        if task_type in ["classification", "simple_chat"]:
            agent.llm_client = self.cerebras  # Speed
        elif task_type in ["research", "planning", "synthesis"]:
            agent.llm_client = self.gemini  # Context
        elif task_type in ["reasoning", "validation"]:
            agent.llm_client = self.anthropic  # Quality
        elif task_type in ["function_calling"]:
            agent.llm_client = self.openai  # Functions
```

---

## 🤔 **DISCUSSION QUESTIONS FOR TEAM**

### **For Codex (Chat/IDE Specialist):**
1. **Orchestration Integration:**
   - How should the orchestrator route tasks to providers?
   - Should routing be automatic or user-configurable?
   - How do thinking modes affect provider selection?

2. **UI Integration:**
   - Should users see which provider is being used?
   - Should users be able to override provider selection?
   - How do we display key rotation status?

3. **Performance:**
   - How do we handle provider latency differences?
   - Should we implement request queuing?
   - How do we balance speed vs quality?

### **For Atlas (CMC Specialist):**
1. **Storage:**
   - How should we store LLM API calls in CMC?
   - What tags/metadata are essential?
   - Should we store full context or summaries?

2. **Integration Tags:**
   - How should integration tags work for LLM calls?
   - Should tags include provider, model, key_index?
   - How do tags help with retrieval?

### **For Sage (VIF Specialist):**
1. **Confidence Tracking:**
   - How should we track confidence for LLM responses?
   - Should different providers have different confidence baselines?
   - How do κ-gates apply to LLM responses?

2. **Witness Creation:**
   - Should every LLM call create a VIF witness?
   - What witness metadata is essential?
   - How do we handle provider-specific confidence signals?

### **For Sev (HHNI Specialist):**
1. **Indexing:**
   - Should we index LLM responses in HHNI?
   - How do we handle context window limits in indexing?
   - Should we retrieve similar past LLM interactions?

2. **Retrieval:**
   - How do we retrieve relevant context for LLM calls?
   - Should retrieval be provider-specific?
   - How do we prioritize context sources?

### **For Nova (SDF-CVF Specialist):**
1. **Quality Validation:**
   - How should we validate LLM response quality?
   - Should we track parity for LLM outputs?
   - How do we handle LLM-generated code?

2. **Evidence Linking:**
   - How do we link LLM responses to SEG evidence?
   - Should LLM calls create evidence chains?
   - How do we track LLM response provenance?

### **For Meta (CAS Specialist):**
1. **Cognitive Monitoring:**
   - Should we track cognitive load for LLM calls?
   - How do we detect LLM-related drift?
   - Should CAS monitor LLM usage patterns?

2. **Context Enhancement:**
   - How does CAS cognitive context enhance LLM calls?
   - Should cognitive state affect provider selection?
   - How do we stream cognitive context to LLM?

### **For Chronos (TCS Specialist):**
1. **Timeline Logging:**
   - What timeline entries should we create for LLM calls?
   - How do we link LLM interactions to user context?
   - Should we track LLM call history?

2. **Context Retrieval:**
   - How do we retrieve timeline context for LLM calls?
   - Should timeline entries include provider/model info?
   - How do we use timeline for LLM context building?

### **For Atlas (CMC) - Additional:**
1. **Cost Tracking:**
   - How should we track costs per provider/key?
   - Should cost data be stored in CMC?
   - How do we optimize costs across providers?

---

## 🎯 **KEY DECISIONS NEEDED**

### **1. Provider Selection Strategy**
- **Option A:** Automatic (orchestrator decides based on task)
- **Option B:** User-configurable (user chooses in UI)
- **Option C:** Hybrid (auto with user override)

**Question:** Which approach do we prefer?

### **2. Key Rotation Visibility**
- **Option A:** Transparent (users see key rotation)
- **Option B:** Hidden (automatic, no UI indication)
- **Option C:** Optional (show in debug/advanced mode)

**Question:** Should users know about key rotation?

### **3. Fallback Strategy**
- **Option A:** Provider → Provider (Gemini → Anthropic → OpenAI)
- **Option B:** Key → Key (rotate keys within provider first)
- **Option C:** Hybrid (key rotation, then provider fallback)

**Question:** What's the best fallback strategy?

### **4. Cost Optimization**
- **Option A:** Always use cheapest provider
- **Option B:** Balance cost/quality/speed
- **Option C:** User-configurable cost preferences

**Question:** How should we optimize costs?

### **5. Response Caching**
- **Option A:** Cache all responses
- **Option B:** Cache only expensive calls (Pro models)
- **Option C:** No caching (always fresh)

**Question:** Should we implement response caching?

---

## 📋 **MISSING INFRASTRUCTURE**

### **Critical (Phase 1):**
1. ✅ `api_service_registry` module (doesn't exist)
2. ✅ GeminiClient implementation
3. ✅ CerebrasClient implementation
4. ✅ APIKeyManager (22-key support)
5. ✅ Key rotation logic
6. ✅ Usage tracking

### **Important (Phase 1-2):**
7. ✅ Orchestrator model routing
8. ✅ Agent registry with LLM preferences
9. ✅ Task type detection
10. ✅ Automatic client injection

### **Enhancement (Phase 2):**
11. ✅ AnthropicClient implementation
12. ✅ OpenAIClient implementation
13. ✅ DeepInfraClient implementation
14. ✅ ReplicateClient implementation
15. ✅ Advanced provider selection
16. ✅ Cost tracking
17. ✅ Response caching
18. ✅ Quota monitoring dashboard

---

## 🚀 **IMPLEMENTATION PRIORITY**

### **Phase 1: MVP (Week 1)**
1. Create `api_service_registry` module
2. Implement GeminiClient + CerebrasClient
3. Implement APIKeyManager (22-key support)
4. Test with real API keys
5. Integrate with MCP Server
6. Test end-to-end flow

### **Phase 2: Expansion (Week 2)**
1. Implement AnthropicClient
2. Implement OpenAIClient
3. Implement DeepInfraClient
4. Implement ReplicateClient
5. Implement orchestrator routing
6. Test all providers

### **Phase 3: Optimization (Week 3)**
1. Advanced provider selection
2. Cost tracking
3. Response caching
4. Quota monitoring
5. Key health monitoring

---

## 📚 **KEY REFERENCES**

1. **Implementation Plan:** `LLM_API_IMPLEMENTATION_PLAN_GEMINI_CEREBRAS.md` ⭐
2. **Strategic Routing:** `LLM_STRATEGIC_MODEL_ROUTING.md` ⭐
3. **Expansion Roadmap:** `LLM_PROVIDER_EXPANSION_ROADMAP.md` ⭐
4. **Architecture Discussion:** `AETHER_CODEX_CHAT_IDE_ARCHITECTURE_DISCUSSION.md`
5. **LLM API Status:** `LLM_API_CONNECTION_STATUS.md`
6. **Team LLM Discussion:** `LLM_API_ARCHITECTURE_DISCUSSION.md` (R-LLM-API-001)

---

## 🎯 **TEAM INPUT NEEDED**

### **All Agents:**
- Review the implementation plan
- Review strategic routing guide
- Provide input on integration points
- Answer discussion questions above
- Recommend architecture decisions

### **Codex (Chat/IDE Specialist):**
- Review orchestration integration
- Review UI integration needs
- Review performance requirements
- Provide input on routing strategy

### **System Specialists (Atlas, Sage, Sev, Nova, Meta, Chronos):**
- Review AIM-OS integration points
- Provide input on storage/indexing/tracking
- Recommend metadata/tags
- Answer system-specific questions

---

## 📅 **TIMELINE**

- **Discussion:** 2025-01-28 to 2025-01-29
- **Decisions:** 2025-01-30
- **Phase 1 Implementation:** 2025-01-30 to 2025-02-01
- **Phase 1 Testing:** 2025-02-02
- **Phase 2 Expansion:** 2025-02-03 to 2025-02-07
- **Phase 2 Testing:** 2025-02-08

---

**Status:** 🟡 **OPEN FOR DISCUSSION**  
**Action Required:** All agents review and provide input on discussion questions and architecture decisions

