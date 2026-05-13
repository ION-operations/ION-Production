# Strategic Model-to-Agent Routing Guide

**Created:** 2025-01-28  
**Source:** Gemini AI Strategic Analysis  
**Status:** ✅ **STRATEGIC GUIDANCE**  
**Purpose:** Guide model selection for different AIM-OS agents and tasks

---

## 🎯 **CORE PRINCIPLE**

**Gemini and Cerebras are not competitive - they are perfectly complementary.**

- **Gemini:** Context-heavy tasks (research, planning, synthesis, reasoning)
- **Cerebras:** Speed-critical tasks (classification, simple chat, tool formatting)

**The Orchestrator becomes a "model router," injecting the correct LLMClient implementation into each agent based on the task.**

---

## 📊 **MODEL-TO-AGENT MAPPING**

| AIM-OS Agent / Task | Recommended API | Model | Rationale |
|---------------------|----------------|-------|-----------|
| **Orchestrator** (Task Classifier) | Cerebras / DeepInfra | Llama 3.1 8B | **Speed.** Classifying user intent is simple, low-context. Need response in milliseconds, not seconds. |
| **ConciseReplyAgent** | Cerebras / DeepInfra | Llama 3.1 8B/70B | **Speed & Low Cost.** Simple chat needs low latency. 22M token/day-per-key pool ideal for high-volume, low-context work. |
| **DeepResearchAgent** | Gemini / Anthropic | 2.5 Pro / Claude 3.5 | **Context Window.** Ingest search results, documents, code. Only Gemini's 1M context or Claude's 200K can handle this. |
| **APOEAgent / SDFAgent** | Gemini / Anthropic | 2.5 Flash / Claude Haiku | **Context Window.** Must "read a set of APOE-related files." Feed all known files and memory entries into large context. |
| **RelationAgent** | Gemini / Anthropic / OpenAI | 2.5 Pro / Claude Opus / GPT-4 | **Reasoning.** Maps APOE↔SDF. Complex synthesis and reasoning over large, structured inputs. Pro/Opus/GPT-4 specialty. |
| **DocAgent** | Gemini / Anthropic / OpenAI | 2.5 Pro / Claude Opus / GPT-4 | **Reasoning & Context.** Merges A+B+C into coherent docs. Needs to synthesize multiple large summaries. Requires large context + strong reasoning. |
| **VerifierAgent** | Gemini / Anthropic / OpenAI | 2.5 Pro / Claude Opus / GPT-4 | **Reasoning.** Sanity-check and flag uncertainties. High-level reasoning task perfect for powerful models. |
| **FunctionCallingAgent** | OpenAI / Anthropic | GPT-4 / Claude 3.5 | **Function Calling.** Tasks requiring tool use, structured outputs, function calling capabilities. |
| **CodeGenerationAgent** | Cerebras / DeepInfra / OpenAI | Llama 3.1 / GPT-4 | **Speed or Quality.** Fast code generation (Cerebras) or high-quality code (GPT-4) based on priority. |

---

## 🔄 **ROUTING STRATEGY**

### **Speed-Critical → Cerebras / DeepInfra**
- Task classification
- Simple chat responses
- Tool formatting
- Low-context operations
- High-volume operations
- Fast inference needs

### **Context-Heavy → Gemini / Anthropic**
- Research with large documents (Gemini 1M context)
- Planning with multiple files (Gemini/Claude)
- Synthesis of multiple sources (Gemini/Claude)
- Complex reasoning (Claude Opus, Gemini Pro)
- Quality-critical validation (Claude, Gemini Pro)

### **Function Calling → OpenAI / Anthropic**
- Tool use tasks
- Structured outputs
- Function calling capabilities
- API integrations

### **Industry Standard → OpenAI**
- Compatibility requirements
- Ecosystem integration
- Wide model support
- Function calling

### **Open Source → Replicate / DeepInfra**
- Custom model needs
- Self-hosted options
- Cost optimization
- Model flexibility

---

## 🏗️ **IMPLEMENTATION PATTERN**

### **LLMClient Abstraction**

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

### **Concrete Implementations**

```python
# GeminiClient - for context-heavy tasks
gemini_client = GeminiClient(key_manager)

# CerebrasClient - for speed-critical tasks
cerebras_client = CerebrasClient(key_manager)
```

### **Orchestrator Routing**

```python
class Orchestrator:
    def __init__(self):
        self.registry = APIServiceRegistry()
        self.gemini = self.registry.get_client("gemini")
        self.cerebras = self.registry.get_client("cerebras")
    
    def route_to_agent(self, task_type: str, agent: Agent):
        """Route appropriate LLM client to agent based on task"""
        if task_type in ["classification", "simple_chat", "tool_formatting"]:
            agent.llm_client = self.cerebras  # Speed-critical
        elif task_type in ["research", "planning", "synthesis", "reasoning"]:
            agent.llm_client = self.gemini  # Context-heavy
        else:
            # Default to Cerebras for speed
            agent.llm_client = self.cerebras
```

---

## 📈 **22-KEY POOL STRATEGY (ALL PROVIDERS)**

### **Provider Free Tier Limits (Per Key):**
- **Gemini Pro:** 50 RPD (Requests Per Day)
- **Gemini Flash:** 250 RPD
- **Anthropic:** Varies by tier (check account limits)
- **OpenAI:** Varies by tier (check account limits)
- **Cerebras:** Varies by tier (check account limits)
- **DeepInfra:** Free tier available (check limits)
- **Replicate:** Varies by tier (check account limits)

### **22-Key Pool Benefits (Per Provider):**
- **Gemini Pro:** 50 × 22 = **1,100 RPD**
- **Gemini Flash:** 250 × 22 = **5,500 RPD**
- **Anthropic:** (varies) × 22 = **Massive combined quota**
- **OpenAI:** (varies) × 22 = **Massive combined quota**
- **Cerebras:** (varies) × 22 = **Massive combined quota**
- **DeepInfra:** (varies) × 22 = **Massive combined quota**
- **Replicate:** (varies) × 22 = **Massive combined quota**

### **Total Combined Capacity:**
- **6 providers × 22 keys = 132 total API keys**
- **Massive combined quota across all providers**
- **Automatic failover between providers**
- **Load balancing across providers and keys**

### **Key Rotation Logic:**
1. Pick a key (e.g., Key_1)
2. Make API call
3. If 429 (Rate Limit Exceeded):
   - Put Key_1 in "cooldown" state
   - Grab next key (Key_2)
   - Retry request
4. Continue until success or all keys exhausted

### **Result:**
- **Robust:** Handles quota exhaustion gracefully
- **Resilient:** Automatic fallback to backup keys
- **High-throughput:** 22-key pool = massive combined quota
- **Abstracted:** Agents don't know or care about key rotation

---

## 🎯 **TASK-SPECIFIC ROUTING EXAMPLES**

### **Example 1: User Asks Simple Question**
```
User: "What is APOE?"
  ↓
Orchestrator: Task type = "simple_chat"
  ↓
Route to: ConciseReplyAgent with CerebrasClient
  ↓
Response: Fast, low-cost, high-volume
```

### **Example 2: User Asks Complex Research Question**
```
User: "How does APOE integrate with CMC? Show me all related files."
  ↓
Orchestrator: Task type = "research"
  ↓
Route to: DeepResearchAgent with GeminiClient
  ↓
Response: Context-heavy, can ingest all files, comprehensive
```

### **Example 3: User Requests Code Generation**
```
User: "Generate a test for APOE CMC integration"
  ↓
Orchestrator: Task type = "code_generation"
  ↓
Route to: CodingAgent with CerebrasClient (speed) OR GeminiClient (quality)
  ↓
Response: Fast (Cerebras) or High-quality (Gemini) based on priority
```

### **Example 4: User Requests Documentation Synthesis**
```
User: "Merge all APOE documentation into one coherent doc"
  ↓
Orchestrator: Task type = "synthesis"
  ↓
Route to: DocAgent with GeminiClient (Pro)
  ↓
Response: Large context + strong reasoning for merging multiple docs
```

---

## 🔧 **INTEGRATION WITH AIM-OS**

### **Agent Registry Pattern**

```python
class AgentRegistry:
    """Registry that specifies which LLM client each agent prefers"""
    
    AGENT_LLM_PREFERENCES = {
        "Orchestrator": "cerebras",  # Speed-critical
        "ConciseReplyAgent": "cerebras",  # Speed-critical
        "DeepResearchAgent": "gemini",  # Context-heavy
        "APOEAgent": "gemini",  # Context-heavy
        "SDFAgent": "gemini",  # Context-heavy
        "RelationAgent": "gemini",  # Reasoning-heavy
        "DocAgent": "gemini",  # Context + reasoning
        "VerifierAgent": "gemini",  # Reasoning-heavy
    }
    
    def get_llm_client(self, agent_name: str) -> LLMClient:
        """Get preferred LLM client for agent"""
        provider = self.AGENT_LLM_PREFERENCES.get(agent_name, "cerebras")
        return api_registry.get_client(provider)
```

---

## 📊 **PERFORMANCE CHARACTERISTICS**

### **Gemini:**
- **Speed:** ~100-200 tokens/sec
- **Context:** 1M tokens (Pro/Flash)
- **Cost:** Higher (but free tier available)
- **Use Case:** Quality-critical, context-heavy

### **Cerebras:**
- **Speed:** ~2000+ tokens/sec (10-20x faster)
- **Context:** 8K tokens (free tier)
- **Cost:** Lower
- **Use Case:** Speed-critical, low-context

### **Combined Strategy:**
- **Best of both worlds:** Speed when needed, quality when needed
- **Cost optimization:** Use Cerebras for high-volume, Gemini for quality
- **Scalability:** 22-key pool overcomes free tier limits

---

## 🚀 **IMPLEMENTATION PRIORITY**

### **Phase 1: Core Infrastructure**
1. LLMClient abstraction
2. GeminiClient implementation
3. CerebrasClient implementation
4. Key pool manager (22-key support)

### **Phase 2: Routing Logic**
1. Orchestrator model routing
2. Agent registry with LLM preferences
3. Task type detection
4. Automatic client injection

### **Phase 3: Optimization**
1. Load balancing across keys
2. Quota monitoring per key
3. Performance metrics tracking
4. Cost tracking per provider

---

## 📚 **REFERENCES**

- **Implementation Plan:** `LLM_API_IMPLEMENTATION_PLAN_GEMINI_CEREBRAS.md`
- **Architecture Discussion:** `AETHER_CODEX_CHAT_IDE_ARCHITECTURE_DISCUSSION.md`
- **API Key Status:** `Testing/artifacts/API_KEY_STATUS.md`
- **Source:** Gemini AI Strategic Analysis (2025-01-28)

---

**Status:** ✅ **STRATEGIC GUIDANCE**  
**Action:** Incorporate into implementation plan and agent routing logic

