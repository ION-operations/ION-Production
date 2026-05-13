# Memory & Context Services Component

**Component of:** Lucid Chat System  
**Purpose:** Chat history, context management, user profiling  
**Status:** 75% (good design, needs refinement)

---

## 🎯 **Quick Context (50 words)**

Memory services manage conversation persistence (CMC storage), context window optimization (4 strategies: recent, relevant via HHNI, sliding, summary), and user personalization (preferences, expertise, interests). Enables long-term memory, intelligent context selection, and personalized AI responses. Token estimation needs accuracy improvement.

---

## 📦 **Files & Structure**

```
memory/
├── ChatHistoryService.ts     # Conversation storage (80%)
├── ContextManager.ts         # Context window management (75%)
├── UserProfileService.ts     # User profiling (75%)
└── index.ts                  # Exports
```

**Total:** 3 files, ~900 lines

---

## 🔧 **Key Classes**

### **ChatHistoryService**
```typescript
class ChatHistoryService {
  async startSession(userId?, title?): Promise<ChatSession>
  async addMessage(message): Promise<ChatMessage>
  getCurrentSession(): ChatSession | null
  async loadSession(sessionId): Promise<ChatSession>
  getRecentMessages(limit): ChatMessage[]
  async searchMessages(query, limit): Promise<ChatMessage[]>
}
```

### **ContextManager**
```typescript
class ContextManager {
  async manageContext(messages, config): Promise<ChatMessage[]>
  private recentStrategy(messages, config): ChatMessage[]
  private async relevantStrategy(messages, config): Promise<ChatMessage[]>
  private slidingStrategy(messages, config): ChatMessage[]
  private async summaryStrategy(messages, config): Promise<ChatMessage[]>
}
```

### **UserProfileService**
```typescript
class UserProfileService {
  async loadProfile(userId): Promise<UserProfile>
  async updatePreferences(preferences): Promise<UserProfile>
  async updateContext(topic, query): Promise<void>
  async addExpertise(domain, level): Promise<void>
  async getRecommendations(): Promise<string[]>
}
```

---

## 📊 **4 Context Strategies**

### **Recent Strategy**
- Keep most recent messages until token limit
- Fast, simple, predictable
- **Use When:** Normal conversations

### **Relevant Strategy** (HHNI-based)
- Semantic search for relevant past messages
- Combines relevant + recent
- **Use When:** Need historical context

### **Sliding Window**
- Fixed window size (last N messages)
- Consistent context size
- **Use When:** Need predictable size

### **Summary Strategy**
- Summarize old messages via LLM
- Keep recent messages full
- **Use When:** Very long conversations

**Auto-selection:** Based on conversation length and complexity

---

## 📊 **Usage Example**

```typescript
import { getChatHistoryService, getContextManager, getUserProfileService } from '../memory'

// Start session
const chatHistory = getChatHistoryService()
const session = await chatHistory.startSession('user123', 'New Chat')

// Add messages
await chatHistory.addMessage({
  role: 'user',
  content: 'Hello!',
})

await chatHistory.addMessage({
  role: 'assistant',
  content: 'Hi! How can I help?',
  metadata: { tokensUsed: 10, confidence: 0.95 },
})

// Manage context window
const contextManager = getContextManager()
const optimized = await contextManager.manageContext(
  session.messages,
  {
    maxTokens: 4000,
    strategy: 'relevant',  // Use HHNI semantic search
  }
)

// Load user profile
const userProfile = getUserProfileService()
const profile = await userProfile.loadProfile('user123')

// Update with conversation context
await userProfile.updateContext('AI assistance', 'Hello')

// Get personalized recommendations
const recommendations = await userProfile.getRecommendations()
```

---

## ⚠️ **Current Issues**

**Token Estimation Inaccurate** ⚠️
- Line 231: `Math.ceil(chars / 4)` is rough estimate
- Not accurate for actual tokenization
- **Impact:** May overflow context windows
- **Fix:** Use tiktoken library (1 day)

**Relevant Strategy Depends on HHNI** ⚠️
- Falls back to recent if HHNI fails
- **Impact:** Strategy may not work as intended
- **Fix:** Ensure HHNI integration validated (1 day)

**Summary Strategy Expensive** ⚠️
- Calls LLM for every summary
- No caching
- **Impact:** High cost for long conversations
- **Fix:** Cache summaries, incremental updates (1 day)

**No Session Persistence** ⚠️
- Session only in memory
- Lost on restart
- **Impact:** No true persistence
- **Fix:** Session restoration from CMC (0.5 days)

**User Profile Doesn't Learn** ⚠️
- Updates context but doesn't analyze patterns
- **Impact:** Limited personalization
- **Fix:** Pattern analysis, ML recommendations (2 days)

**Tests:** 0 / ~10 needed

---

## 🎯 **Integration Points**

**Upstream:**
- CMC - Store messages, sessions, profiles
- HHNI - Relevant strategy, message search
- LLM - Summary generation

**Downstream:**
- AdvancedLLMService - Context optimization before requests
- UI - Display chat history
- User settings - Preference management

---

## 🚀 **Next Steps**

1. Implement accurate token counting with tiktoken (1 day)
2. Validate HHNI integration (1 day)
3. Add summary caching (1 day)
4. Implement session persistence (0.5 days)
5. Add pattern learning to user profiles (2 days)
6. Write comprehensive tests (1 day)

**Effort to Production:** ~6.5 days

---

**Parent:** [../../L2_architecture.md](../../L2_architecture.md)  
**Implementation:** `ide_orchestration/prototypes/dac/src/services/lucid-chat/memory/`

