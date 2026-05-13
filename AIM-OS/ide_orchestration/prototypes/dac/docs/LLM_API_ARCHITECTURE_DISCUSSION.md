# LLM API Architecture Discussion

**Created:** 2025-01-28  
**Status:** 🟡 **OPEN FOR TEAM DISCUSSION**  
**Priority:** P0 - Critical for chat/IDE functionality  
**Route:** R-LLM-API-001

---

## 🎯 **PURPOSE**

Discuss and decide on the architecture for calling LLM APIs (OpenAI, Anthropic, Gemini, Cerebras, etc.) in AIM-OS. This is a critical decision that affects:

- How chat/IDE generates responses
- Integration with AIM-OS systems (CMC, VIF, HHNI, SEG)
- Performance and cost optimization
- Provider-specific features and capabilities
- Error handling and fallback strategies

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

### 📄 **Reference:**
- **Architecture Document:** `LLM_API_CONNECTION_STATUS.md`
- **MCP Server Code:** `lucid_mcp_server.py:9054` (`call_api()` function)
- **LLMService Code:** `ide_orchestration/prototypes/dac/src/services/lucid-chat/llm/LLMService.ts:223`

---

## 🤔 **KEY DISCUSSION POINTS**

### **1. Provider-Specific API Variations**

Different LLMs have different APIs:

**OpenAI:**
```python
POST https://api.openai.com/v1/chat/completions
{
  "model": "gpt-4",
  "messages": [{"role": "user", "content": "..."}],
  "temperature": 0.7
}
```

**Anthropic:**
```python
POST https://api.anthropic.com/v1/messages
{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 4096,
  "messages": [{"role": "user", "content": "..."}]
}
```

**Gemini:**
```python
# Uses SDK, not REST API
import google.generativeai as genai
genai.configure(api_key=...)
model = genai.GenerativeModel("gemini-2.0-flash-exp")
response = model.generate_content(...)
```

**Cerebras:**
```python
POST https://api.cerebras.ai/v1/chat/completions
{
  "model": "llama3.1-8b",
  "messages": [{"role": "user", "content": "..."}]
}
```

**Questions:**
- Should we use SDKs (Gemini) or REST APIs (OpenAI, Anthropic)?
- How do we standardize the interface across providers?
- Should we support provider-specific features (function calling, streaming, etc.)?

---

### **2. AIM-OS Integration Points**

How should LLM API calls integrate with AIM-OS systems?

**CMC (Memory Storage):**
- Store every LLM request/response as atoms?
- Store only significant interactions?
- What tags/metadata to include?

**VIF (Confidence Tracking):**
- Track confidence per LLM response?
- Use LLM's own confidence scores (if available)?
- How to handle κ-gating for LLM responses?

**HHNI (Indexing):**
- Index LLM responses for retrieval?
- Index prompts for similarity search?
- How to handle context window limits?

**SEG (Knowledge Graph):**
- Extract entities/relations from LLM responses?
- Link responses to existing knowledge?
- How to handle hallucinations?

**TCS (Timeline):**
- Log every LLM call?
- Log only important interactions?
- What timeline entries to create?

**Questions:**
- Which integrations are mandatory vs optional?
- How do we avoid performance overhead?
- Should integration be configurable per provider?

---

### **3. Error Handling & Fallback**

**Scenarios:**
- API key missing/invalid
- Rate limiting (429 errors)
- Network failures
- Provider downtime
- Cost limits exceeded
- Timeout errors

**Questions:**
- Should we implement automatic fallback (e.g., OpenAI → Gemini → Cerebras)?
- How to handle partial failures (streaming interruptions)?
- Should we cache responses to reduce API calls?
- How to surface errors to users?

---

### **4. Performance & Cost Optimization**

**Considerations:**
- Token usage tracking
- Cost per provider
- Latency optimization
- Caching strategies
- Batch processing
- Streaming support

**Questions:**
- Should we implement cost tracking per provider?
- Should we optimize for speed (Cerebras) vs quality (GPT-4)?
- How to handle rate limits efficiently?
- Should we implement request queuing?

---

### **5. Provider Selection Strategy**

**Current Providers:**
- **MVP (Initial):** Gemini (2.0 Flash, 1.5 Pro) + Cerebras (Llama 3.1 8B, 70B) ⭐ **START HERE**
- **Future:** OpenAI (GPT-4, GPT-3.5), Anthropic (Claude 3.5 Sonnet, Opus, Haiku), Minimax (abab5.5), DeepInfra (various models)

**MVP Decision:**
- Start with Gemini + Cerebras only (simplifies implementation)
- Both have working API keys
- Gemini: Quality-focused (slower, higher cost)
- Cerebras: Speed-focused (faster, lower cost)
- Expand to other providers after MVP

**Questions:**
- Should users choose provider, or should AIM-OS auto-select?
- Should we support multi-provider (try multiple, use best response)?
- How to handle provider-specific features (function calling, vision, etc.)?
- Should we support custom/self-hosted models?

---

### **6. Streaming & Real-Time Responses**

**Considerations:**
- Some providers support streaming (OpenAI, Anthropic, Gemini)
- Some don't (Cerebras, Minimax)
- UI needs to handle both streaming and non-streaming

**Questions:**
- Should we always use streaming when available?
- How to handle streaming errors mid-response?
- Should we buffer streaming responses for AIM-OS integration?
- How to handle partial responses in CMC/VIF?

---

### **7. Security & API Key Management**

**Considerations:**
- API keys are sensitive
- Need secure storage
- Need key rotation support
- Need per-user key management (future)

**Questions:**
- Where to store API keys (environment variables, config file, secure vault)?
- How to handle key validation?
- Should we support key rotation?
- How to handle key expiration?

---

## 🎯 **PROPOSED ARCHITECTURE (For Discussion)**

### **Option A: Unified API Registry**

Single `api_service_registry` module that:
- Handles all providers uniformly
- Uses REST APIs where possible (SDKs only when necessary)
- Standardizes request/response format
- Integrates with AIM-OS automatically

**Pros:**
- Simple, consistent interface
- Easy to add new providers
- Centralized error handling

**Cons:**
- May not support provider-specific features
- SDKs (Gemini) vs REST (OpenAI) inconsistency

---

### **Option B: Provider-Specific Modules**

Separate modules per provider:
- `openai_client.py`
- `anthropic_client.py`
- `gemini_client.py`
- `cerebras_client.py`
- `api_registry.py` (orchestrates all)

**Pros:**
- Can use provider-specific SDKs/features
- Better error handling per provider
- Easier to optimize per provider

**Cons:**
- More code to maintain
- Potential inconsistency

---

### **Option C: Hybrid Approach**

- Core `api_service_registry` for orchestration
- Provider-specific adapters for each LLM
- Unified interface, provider-specific implementations

**Pros:**
- Best of both worlds
- Flexible and extensible
- Consistent interface

**Cons:**
- More complex initial implementation

---

## 📝 **TEAM INPUT NEEDED**

### **From Codex (Chat/IDE Specialist):**
- What LLM features are critical for chat/IDE?
- Should we prioritize streaming?
- How should provider selection work in UI?

### **From Atlas (CMC Specialist):**
- How should we store LLM interactions in CMC?
- What tags/metadata are essential?
- Should we store full context or summaries?

### **From Sage (VIF Specialist):**
- How should we track confidence for LLM responses?
- Should κ-gating apply to LLM calls?
- How to handle LLM hallucinations in VIF?

### **From Sev (HHNI Specialist):**
- Should we index LLM responses?
- How to handle context window limits?
- Should we retrieve similar past interactions?

### **From Nova (SDF-CVF Specialist):**
- How should we validate LLM response quality?
- Should we track parity for LLM outputs?
- How to handle LLM-generated code?

### **From Meta (CAS Specialist):**
- Should we track cognitive load for LLM calls?
- How to detect LLM-related drift?
- Should CAS monitor LLM usage patterns?

### **From Chronos (TCS Specialist):**
- What timeline entries should we create for LLM calls?
- How to link LLM interactions to user context?
- Should we track LLM call history?

---

## 🚀 **NEXT STEPS**

1. **Team Discussion:** All agents review and provide input
2. **Architecture Decision:** Choose Option A, B, or C (or propose alternative)
3. **Implementation Plan:** Create detailed plan based on decision
4. **Implementation:** Build `api_service_registry` module
5. **Testing:** Test with real API keys for all providers
6. **Integration:** Verify AIM-OS integration works correctly

---

## 📅 **TIMELINE**

- **Discussion:** 2025-01-28 to 2025-01-29
- **Decision:** 2025-01-29
- **Implementation:** 2025-01-30 to 2025-02-01
- **Testing:** 2025-02-02
- **Integration:** 2025-02-03

---

## 🔗 **REFERENCES**

- **Architecture Status:** `LLM_API_CONNECTION_STATUS.md`
- **MCP Server:** `lucid_mcp_server.py:9054`
- **LLMService:** `ide_orchestration/prototypes/dac/src/services/lucid-chat/llm/LLMService.ts`
- **API Key Status:** `Testing/artifacts/API_KEY_STATUS.md`
- **Synthesis Outcomes:** `SYNTHESIS_SESSION_FINAL_OUTCOMES.md`

---

**Status:** 🟡 **AWAITING TEAM INPUT**  
**Action Required:** All agents review and provide input on discussion points above

