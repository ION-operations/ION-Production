# 🤝 Agent Check-In Protocol - MCP Welcome System

**Created:** 2025-11-06  
**Status:** ✅ **ACTIVE**  
**Purpose:** Automatically direct new agents to onboarding files via MCP  
**Trigger:** Agent sends check-in message via MCP

---

## 🎯 **CHECK-IN FLOW**

### **When Agent Checks In:**

**Agent sends:**
```json
{
  "tool": "send_ai_message",
  "arguments": {
    "from_ai": "Max",  # or "Lex", "Sam", "Dac"
    "to_ai": "Aether",
    "content": "Checking in - ready to start work",
    "message_type": "status_update",
    "thread_id": "north-star-orchestration-2025-11-06"
  }
}
```

**Aether responds with:**
1. Welcome message
2. Direct links to onboarding files
3. Assignment confirmation
4. Quick start instructions

---

## 📋 **AUTOMATED WELCOME MESSAGE**

**Template:**

```
🤝 WELCOME TO NORTH STAR PROJECT!

**Your Assignment:**
- {Agent Name}: {Part Name} (Ch{XX}-Ch{YY})
- Chapters: {list chapters}

**ESSENTIAL READING (Read These First!):**
1. **CURSOR_AGENT_ONBOARDING.md** - Complete onboarding guide
   📁 `north_star_project/CURSOR_AGENT_ONBOARDING.md`
   
2. **MULTI_AGENT_WORKFLOW.md** - 3-pass workflow system
   📁 `north_star_project/MULTI_AGENT_WORKFLOW.md`
   
3. **QUICK_REFERENCE.md** - Daily reference guide
   📁 `north_star_project/QUICK_REFERENCE.md`

**CRITICAL REMINDERS:**
- ✅ Quality metrics, NOT word counts!
- ✅ First pass only (~500-800 words, scaffolds)
- ✅ Initialize quality gates as "pending"
- ✅ Codex calculates scores and expands

**Your First Task:**
1. Read CURSOR_AGENT_ONBOARDING.md (15 minutes)
2. Check your assignment (which chapters?)
3. Check dependencies (what needs to complete first?)
4. Start first chapter scaffold

**Questions?** Ask in SHARED_MESSAGE_BOARD.md or send MCP message.

**Ready to start?** Confirm after reading onboarding files!
```

---

## 🔄 **CHECK-IN RESPONSES BY AGENT**

### **Max (Part I - Wave 1):**
```
**Your Assignment:**
- Part I: The Awakening (Ch01-Ch04)
- Current Status:
  - Ch01: Scaffold exists (~1,840 words), needs quality assessment
  - Ch02: Scaffold exists (~2,057 words), needs quality assessment
  - Ch03: Scaffold exists (~745 words), needs expansion
  - Ch04: Scaffold exists (~1,504 words), needs quality assessment

**Priority:** Complete quality assessment for Wave 1 chapters (Ch01, Ch02, Ch04)
**Dependencies:** None - Wave 1 has no dependencies!
**Next:** After Wave 1 quality assessment, expand Ch03
```

### **Lex (Part II - Foundation):**
```
**Your Assignment:**
- Part II: The Foundation (Ch05-Ch10)
- Current Status:
  - Ch05 (CMC): Scaffold exists (~689 words), blocked by Wave 1
  - Ch06 (HHNI): Scaffold exists (~473 words), blocked by Wave 1
  - Ch07 (VIF): Scaffold exists (~645 words), blocked by Wave 1
  - Ch08 (APOE): Scaffold exists (~512 words), blocked by Wave 1
  - Ch09 (SEG): Scaffold exists (~401 words), blocked by Wave 1
  - Ch10 (SDF-CVF): Scaffold exists (~628 words), blocked by Wave 1

**Priority:** Wait for Wave 1 completion, then expand all Part II chapters
**Dependencies:** Wave 1 (Ch01, Ch02, Ch04) must complete first
**Next:** Once Wave 1 complete, start expanding Ch05 (CMC)
```

### **Sam (Part III - Consciousness):**
```
**Your Assignment:**
- Part III: The Consciousness (Ch11-Ch15)
- Current Status:
  - Ch11 (CAS): Scaffold exists (~585 words), blocked by Part II
  - Ch12 (SIS): Scaffold exists (~513 words), blocked by Part II
  - Ch13 (CCS): Scaffold exists (~537 words), blocked by Part II
  - Ch14 (MIGE): Scaffold exists (~554 words), blocked by Part II
  - Ch15 (ARD): Scaffold exists (~523 words), blocked by Part II

**Priority:** Wait for Part II completion, then expand all Part III chapters
**Dependencies:** Part II (Ch05-Ch10) must complete first
**Next:** Once Part II complete, start expanding Ch11 (CAS)
```

### **Dac (Part IV-VII - Authority + Math + Builder + Reference):**
```
**Your Assignment:**
- Part IV-VII: Authority + Mathematics + Builder + Reference (Ch16-Ch40)
- Current Status:
  - Ch16-Ch19: Scaffolds exist, some quality gates passing
  - Ch20-Ch23: Scaffolds exist
  - Ch24-Ch27: Scaffolds exist
  - Ch28-Ch40: Scaffolds exist

**Priority:** Check dependencies per chapter (see ChainSpec.yaml)
**Dependencies:** Vary by chapter (check ChainSpec.yaml)
**Next:** Start with chapters that have no dependencies
```

---

## 📚 **ONBOARDING FILE CHECKLIST**

**When agent checks in, confirm they've read:**

- [ ] CURSOR_AGENT_ONBOARDING.md
- [ ] MULTI_AGENT_WORKFLOW.md
- [ ] QUICK_REFERENCE.md
- [ ] gates.json (understand quality_assessment gate)
- [ ] ChainSpec.yaml (understand their chapters)

**If not read:**
- Direct them to read first
- Don't assign work until onboarding complete

---

## 🎯 **FIRST TASK ASSIGNMENT**

**After onboarding confirmed:**

**Agent 1:**
- Task: Run quality assessment on Wave 1 chapters (Ch01, Ch02, Ch04)
- Reference: `INTELLIGENT_QUALITY_METRICS_DESIGN.md`
- Goal: Calculate quality scores, identify gaps

**Agent 2:**
- Task: Review Part II scaffolds, prepare for expansion
- Reference: `NORTH_STAR_INTEGRATION_VALIDATION.md` (Part II section)
- Goal: Understand Tier A sources, prepare expansion plan

**Agent 3:**
- Task: Review Part III scaffolds, prepare for expansion
- Reference: `NORTH_STAR_INTEGRATION_VALIDATION.md` (Part III section)
- Goal: Understand Tier A sources, prepare expansion plan

**Agent 4:**
- Task: Check dependencies, start with available chapters
- Reference: `ChainSpec.yaml` (check dependencies per chapter)
- Goal: Start first-pass scaffolds on chapters with no dependencies

---

## 💬 **MCP MESSAGE TEMPLATES**

### **Welcome Message (Aether → New Agent):**
```json
{
  "tool": "send_ai_message",
  "arguments": {
    "from_ai": "Aether",
    "to_ai": "Max",  # or "Lex", "Sam", "Dac"
    "content": "{Welcome message with onboarding links}",
    "message_type": "status_update",
    "priority": "high",
    "thread_id": "north-star-orchestration-2025-11-06"
  }
}
```

### **Assignment Confirmation (Agent → Aether):**
```json
{
  "tool": "send_ai_message",
  "arguments": {
    "from_ai": "Max",  # or "Lex", "Sam", "Dac"
    "to_ai": "Aether",
    "content": "Onboarding complete. Ready to start {chapter_id}. Confirming assignment: {Part Name} (Ch{XX}-Ch{YY})",
    "message_type": "status_update",
    "thread_id": "north-star-orchestration-2025-11-06"
  }
}
```

### **First Task Start (Agent → Aether):**
```json
{
  "tool": "send_ai_message",
  "arguments": {
    "from_ai": "Max",  # or "Lex", "Sam", "Dac"
    "to_ai": "Aether",
    "content": "Starting first pass on {chapter_id}. Pre-flight checks passed. Creating scaffold.",
    "message_type": "status_update",
    "thread_id": "north-star-orchestration-2025-11-06"
  }
}
```

---

## ✅ **CHECK-IN VALIDATION**

**Before assigning work, verify:**
- ✅ Agent has read onboarding files
- ✅ Agent understands quality metrics (not word counts)
- ✅ Agent knows their assignment
- ✅ Agent understands dependencies
- ✅ Agent knows first pass workflow

**If any missing:**
- Direct to appropriate file
- Don't assign work until validated

---

## 🚨 **COMMON CHECK-IN QUESTIONS**

**Q: "What chapters am I assigned?"**
- A: See assignment section above + CURSOR_AGENT_ONBOARDING.md

**Q: "What's my first task?"**
- A: See "First Task Assignment" section above

**Q: "Where are the onboarding files?"**
- A: All in `north_star_project/` directory:
  - CURSOR_AGENT_ONBOARDING.md
  - MULTI_AGENT_WORKFLOW.md
  - QUICK_REFERENCE.md

**Q: "What's the quality metrics system?"**
- A: Read `INTELLIGENT_QUALITY_METRICS_DESIGN.md` + `gates.json`

**Q: "Can I start work immediately?"**
- A: After reading onboarding files, yes! Start with first pass scaffolds.

---

## 📊 **TRACKING AGENT CHECK-INS**

**Update STATUS_TRACKER.md when agent checks in:**
- Agent name
- Check-in timestamp
- Onboarding status
- Assignment confirmed
- First task assigned

**Example:**
```
- 2025-11-06 16:45 — Max checked in via MCP
  - Onboarding: Complete
  - Assignment: Part I (Ch01-Ch04) confirmed
  - First task: Quality assessment on Wave 1 chapters
  - Status: Ready to start
```

---

**Status:** ✅ **ACTIVE**  
**Purpose:** Automatically direct agents to onboarding via MCP  
**Files:** All onboarding files in `north_star_project/` directory

