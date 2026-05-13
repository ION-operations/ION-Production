# Lucid Chat API - Quick Reference

**Version:** 0.9.2  
**Status:** Production Ready

---

## 🚀 **QUICK START**

### **Basic Chat:**
```typescript
import { LLMService } from './llm/LLMService'

const service = new LLMService()
const response = await service.chatCompletion({
  provider: 'anthropic',
  messages: [{ role: 'user', content: 'Hello!' }]
})
```

### **Advanced Chat:**
```typescript
import { AdvancedLLMService } from './llm/AdvancedLLMService'

const service = new AdvancedLLMService()
const response = await service.advancedChatCompletion({
  messages: [{ role: 'user', content: 'Research quantum computing' }],
  thinkingMode: { mode: 'analytical' },
  deepSearch: { providers: ['deepsearch', 'perplexity'], depth: 'comprehensive' }
})
```

---

## 📋 **SERVICE INDEX**

### **LLM Services:**
- `LLMService` - Basic LLM chat completion
- `AdvancedLLMService` - Advanced chat with thinking modes, deep search, APOE

### **Search Services:**
- `DeepSearchService` - DEEPSEARCH sovereign intelligence
- `ICIPSearchService` - ICIP semantic code search
- `SearchOrchestrator` - Multi-provider search orchestration

### **Reasoning Services:**
- `BranchReasoningService` - Multi-path branch reasoning

### **Research Services:**
- `ARDService` - Autonomous Research Dream

### **Agent Services:**
- `AgentRegistry` - Agent registration and management
- `MultiAgentOrchestrator` - Multi-agent collaboration

### **Memory Services:**
- `ChatHistoryService` - Chat history management
- `ContextManager` - Context window management
- `UserProfileService` - User profiling

### **Orchestration Services:**
- `WorkflowExecutor` - APOE workflow execution
- `BudgetTracker` - Budget tracking
- `QualityGates` - Quality gate enforcement
- `DAGExecutor` - DAG parallel execution

### **Validation Services:**
- `InputValidator` - Input validation
- `SecurityValidator` - Security validation

### **Recovery Services:**
- `RetryManager` - Retry with backoff
- `CircuitBreaker` - Circuit breaker pattern
- `ErrorRecovery` - Error recovery orchestration

### **Cache Services:**
- `CacheManager` - In-memory caching
- `RateLimiter` - Rate limiting

### **Security Services:**
- `Authentication` - API key authentication
- `Authorization` - Role-based authorization

---

## 🔑 **AUTHENTICATION**

```typescript
import { Authentication } from './security/Authentication'

const result = Authentication.authenticate(apiKey, {
  requireAuth: true,
  apiKey: process.env.API_KEY
})
```

---

## 📖 **FULL DOCUMENTATION**

See `knowledge_architecture/systems/lucid-chat/API_DOCUMENTATION.md` for complete documentation.

---

**Status:** ✅ **COMPLETE**  
**Version:** 0.9.2


