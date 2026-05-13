# LLM Services Component

**Component of:** Lucid Chat System  
**Purpose:** Unified LLM provider interface with advanced capabilities  
**Status:** 80% (framework solid, needs SEG/VIF/CAS validation)

---

## 🎯 **Quick Context (50 words)**

LLM services provide unified interface to 7+ providers (Anthropic, OpenAI, Gemini, DeepSeek, Cerebras, Minimax, etc.). AdvancedLLMService adds thinking mode auto-configuration, deep search integration, APOE orchestration, branch reasoning, prompt engineering (style, tone, format, CoT), and complete AIM-OS metadata. Handles provider routing, error recovery, retries.

---

## 📦 **Files & Structure**

```
llm/
├── LLMService.ts             # Base LLM service (85%)
├── AdvancedLLMService.ts     # Advanced features (80%)
├── MinimaxService.ts         # Minimax provider (90%)
├── GeminiClient.ts           # Gemini provider (90%)
└── AnthropicClient.ts        # Anthropic provider (90%)
```

**Backend:**
```
packages/llm_client/
├── __init__.py               # Base client
├── anthropic.py              # Anthropic client
├── gemini.py                 # Gemini client
└── cerebras.py               # Cerebras client
```

**Total:** 5 frontend + 4 backend files, ~3,000 lines

---

## 🔧 **Key Classes**

### **LLMService**
```typescript
class LLMService extends BaseAPIService {
  async chatCompletion(request: LLMChatRequest): Promise<APIResponse<LLMResponse>>
  async complete(prompt, provider, model?, temperature?, maxTokens?): Promise<...>
  async getAvailableModels(): Promise<string[]>
  isAvailable(): boolean
}
```

**Status:** 85% (works well)

### **AdvancedLLMService**
```typescript
class AdvancedLLMService extends LLMService {
  async advancedChatCompletion(request: AdvancedLLMRequest): Promise<AdvancedLLMResponse>
  
  private async applyThinkingMode(request): Promise<AdvancedLLMRequest>
  private shouldUseBranchReasoning(request): boolean
  private async performDeepSearch(request): Promise<DeepSearchResults>
  private async buildAdvancedPrompt(request): Promise<Message[]>
  private async chatCompletionViaAPOE(request, messages): Promise<...>
  private async synthesizeKnowledgeViaSEG(request): Promise<void>
}
```

**Status:** 80% (configuration works, needs integration validation)

---

## 📊 **Thinking Mode Auto-Configuration**

**Creative Mode (Temp: 0.9):**
- APOE: Planner + Builder
- Search: Perplexity + DEEPSEARCH (advanced)
- SEG: Disabled (speed priority)
- CAS: 0.60 load limit

**Analytical Mode (Temp: 0.3):**
- APOE: Retriever + Reasoner + Critic + Verifier
- Search: All 4 providers (comprehensive)
- SEG: Enabled + contradiction detection
- CAS: 0.85 load limit
- Branch Reasoning: Auto-activated

**Balanced Mode (Temp: 0.7):**
- APOE: Planner + Retriever + Reasoner + Builder
- Search: DEEPSEARCH + Perplexity (advanced)
- SEG: Enabled
- CAS: 0.70 load limit

**Reasoning Mode (Temp: 0.2):**
- APOE: Retriever + Reasoner + Verifier + Critic
- Search: DEEPSEARCH + ICIP + Tavily (comprehensive)
- SEG: Enabled + strong evidence
- VIF: 0.90 threshold, witness required
- CAS: 0.90 load limit
- Branch Reasoning: Auto-activated

**Intuitive Mode (Temp: 0.8):**
- APOE: Builder only (fast)
- Search: Perplexity (basic)
- SEG: Disabled
- CAS: 0.50 load limit

---

## 📊 **Usage Examples**

### **Basic Chat:**
```typescript
const llmService = new LLMService()

const response = await llmService.chatCompletion({
  provider: 'anthropic',
  messages: [{ role: 'user', content: 'Hello!' }],
  temperature: 0.7,
})
```

### **Advanced Chat with Auto-Configuration:**
```typescript
const advancedService = getAdvancedLLMService()

const response = await advancedService.advancedChatCompletion({
  provider: 'anthropic',
  messages: [{ role: 'user', content: 'Complex problem...' }],
  thinkingMode: { mode: 'analytical' },  // Auto-configures everything!
})

// Behind the scenes:
// - Temperature: 0.3
// - APOE: 4 roles (Retriever, Reasoner, Critic, Verifier)
// - Search: 4 providers (DEEPSEARCH, ICIP, Perplexity, Tavily)
// - SEG: Enabled with contradictions
// - VIF: 0.80 threshold
// - CAS: 0.85 load limit
// - Branch Reasoning: Auto-activated (if complex)
```

### **Full Control:**
```typescript
const response = await advancedService.advancedChatCompletion({
  provider: 'anthropic',
  model: 'claude-3-5-sonnet-20241022',
  messages: [...],
  temperature: 0.5,
  apoe: {
    useAPOE: true,
    roles: [{ role: 'reasoner' }, { role: 'builder' }],
  },
  deepSearch: {
    providers: ['deepsearch', 'icip'],
    depth: 'comprehensive',
  },
  seg: {
    useSEG: true,
    detectContradictions: true,
  },
  vif: {
    useVIF: true,
    confidenceThreshold: 0.90,
  },
})
```

---

## ⚠️ **Current Issues**

**SEG/VIF/CAS Configuration Not Validated** ⚠️
- Lines 415-453: Creates config objects
- But these systems don't actually accept these parameters
- **Impact:** Configuration may do nothing
- **Fix:** Validate integration or remove claims (2 days)

**Branch Reasoning Trigger Heuristic** ⚠️
- Uses keyword matching for complexity detection
- May miss or over-trigger
- **Fix:** Better complexity analysis (1 day)

**No Streaming Support** ⚠️
- All responses wait for completion
- No progressive rendering
- **Impact:** Long waits for complex tasks
- **Fix:** Implement streaming (Phase 3)

**Tests:** 0 / ~20 needed

---

## 🎯 **Integration Points**

**Upstream:**
- LLM Providers - Via API Service Registry
- APOE - Workflow orchestration
- Search - Deep search providers
- Branch Reasoning - Multi-path exploration
- CMC/HHNI/VIF/SEG - Consciousness integration
- MCP Tools - Via Command Server

**Downstream:**
- UI Components - Chat interface
- AdvancedLLMService - Primary user interface
- All other services - Use for LLM calls

---

## 🚀 **Next Steps**

1. Validate SEG/VIF/CAS integration (2 days)
2. Improve complexity detection for branch reasoning (1 day)
3. Add streaming support (Phase 3)
4. Write comprehensive tests (2 days)

**Effort to Production:** ~5 days (excluding streaming)

---

**Parent:** [../../L2_architecture.md](../../L2_architecture.md)  
**Implementation:** `ide_orchestration/prototypes/dac/src/services/lucid-chat/llm/`

