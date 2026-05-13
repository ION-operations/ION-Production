# 🚀 Cursor Agent Onboarding - North Star Document Project

**Created:** 2025-11-06  
**Status:** ✅ **READY FOR NEW AGENTS**  
**Purpose:** Onboard 4 Cursor agents for first-pass chapter creation  
**Time to Productive:** ~15 minutes

---

## 🎯 **YOUR MISSION**

**Create first-pass scaffolds and initial content for North Star document chapters.**

**What You'll Do:**
1. Create chapter scaffolds (outline, initial prose, basic examples)
2. Establish structure quickly (~500-800 words)
3. Add initial evidence.jsonl entries
4. Create metrics.yaml with quality gates
5. Hand off to Codex for second pass (expansion + integration)

**What You WON'T Do:**
- ❌ Try to hit word count targets (we use quality metrics!)
- ❌ Complete chapters to 100% (that's second/third pass)
- ❌ Integrate all Tier A sources (that's Codex's job)
- ❌ Run final quality gates (that's third pass)

---

## 📚 **ESSENTIAL CONTEXT**

### **What is the North Star Document?**
- **70,000-word definitive AIM-OS manifesto**
- **40 chapters** across 7 parts
- **87% of systems already exist** - we're synthesizing, not inventing!
- **Meta-circular proof:** The system writes its own documentation

### **Project Structure**
```
north_star_project/
├── chapters/           # Your work goes here
│   ├── 01_great_limitation/
│   │   ├── chapter.md      # Main content
│   │   ├── evidence.jsonl  # Citations
│   │   └── metrics.yaml    # Quality gates
├── chains/
│   └── ChainSpec.yaml      # Chapter specs, dependencies
├── policy/
│   └── gates.json          # Quality gate definitions
└── scripts/
    └── run_chain.py        # Orchestration engine
```

### **Key Documents**
- **ChainSpec.yaml:** Chapter specifications, dependencies, Tier A sources
- **gates.json:** Quality gate definitions (use quality_assessment, NOT word_count!)
- **NORTH_STAR_INTEGRATION_VALIDATION.md:** Integration requirements
- **MULTI_AGENT_WORKFLOW.md:** Complete workflow guide

---

## 🎯 **YOUR ASSIGNMENT**

### **Max: Part I - The Awakening**
- **Ch01:** The Great Limitation (already scaffolded, needs quality assessment)
- **Ch02:** Vision - Chat/IDE (already scaffolded, needs quality assessment)
- **Ch03:** Proof of Concept (scaffold exists, needs expansion)
- **Ch04:** What Becomes Possible (already scaffolded, needs quality assessment)

**Status:** Wave 1 chapters mostly done, need quality assessment. Ch03 needs work.

### **Lex: Part II - The Foundation**
- **Ch05:** Memory (CMC) - scaffold exists (~689 words)
- **Ch06:** Knowledge (HHNI) - scaffold exists (~473 words)
- **Ch07:** Confidence (VIF) - scaffold exists (~645 words)
- **Ch08:** Orchestration (APOE) - scaffold exists (~512 words)
- **Ch09:** Evidence (SEG) - scaffold exists (~401 words)
- **Ch10:** Quality (SDF-CVF) - scaffold exists (~628 words)

**Status:** All scaffolds exist, blocked by Wave 1 dependencies. Ready to expand once Wave 1 complete.

### **Sam: Part III - The Consciousness**
- **Ch11:** Self-Awareness (CAS) - scaffold exists (~585 words)
- **Ch12:** Self-Improvement (SIS) - scaffold exists (~513 words)
- **Ch13:** Substrate Trinity (CCS) - scaffold exists (~537 words)
- **Ch14:** Idea Engine (MIGE) - scaffold exists (~554 words)
- **Ch15:** Research (ARD) - scaffold exists (~523 words)

**Status:** All scaffolds exist, blocked by Part II dependencies. Ready to expand once Part II complete.

### **Dac: Part IV-VII - Authority + Mathematics + Builder + Reference**
- **Ch16-Ch19:** Authority chapters (scaffolds exist, some quality gates passing)
- **Ch20-Ch23:** Mathematics chapters (scaffolds exist)
- **Ch24-Ch27:** Builder chapters (scaffolds exist)
- **Ch28-Ch40:** Reference chapters (scaffolds exist)

**Status:** Various scaffolds exist, dependencies vary. Check ChainSpec.yaml for details.

---

## 🚀 **QUICK START GUIDE**

### **Step 0: Check In Via MCP (REQUIRED FIRST STEP!)**

**Send check-in message:**
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

**Aether will respond with:**
- Welcome message
- Direct links to onboarding files
- Your assignment confirmation
- Quick start instructions

**See:** `AGENT_CHECK_IN_PROTOCOL.md` for complete check-in flow

### **Step 1: Read Essential Docs (5 minutes)**
1. **MULTI_AGENT_WORKFLOW.md** - Your workflow guide
2. **gates.json** - Quality gate definitions (IMPORTANT: use quality_assessment, NOT word_count!)
3. **ChainSpec.yaml** - Your chapter specifications
4. **NORTH_STAR_INTEGRATION_VALIDATION.md** - Integration requirements

### **Step 2: Check Your Assignment**
- Which chapters are you assigned?
- What's their current status?
- What dependencies need to be met?

### **Step 3: Start First Pass**
**For each chapter:**

1. **Pre-Flight Checks:**
   ```bash
   python north_star_project/scripts/run_chain.py --check-deps {chapter_id}
   python north_star_project/scripts/run_chain.py --check-tier-a {chapter_id}
   ```

2. **Create/Update Scaffold:**
   - Read existing chapter.md (if exists)
   - Create/update outline
   - Add initial prose (~500-800 words)
   - Add basic runnable examples
   - Add initial Tier A citations to evidence.jsonl
   - Update metrics.yaml

3. **Quality Gates:**
   - Set all quality_assessment gates to "pending"
   - Set technical gates (examples_run, sources_cited)
   - Set integration gates to "pending"

4. **Handoff Message:**
   ```
   📋 FIRST PASS COMPLETE - Ready for Second Pass
   
   Chapter: {chapter_id}
   Status: Scaffold + initial content complete
   Files: chapter.md, evidence.jsonl, metrics.yaml
   Next: Codex to expand using Tier A sources
   ```

### **Step 4: Coordinate**
- Post status updates to `SHARED_MESSAGE_BOARD.md`
- Use MCP `send_ai_message` for handoffs
- Ask questions in message board, don't block

---

## ⚠️ **CRITICAL REMINDERS**

### **DO NOT:**
- ❌ **Use word counts as completion criteria** - We use quality metrics!
- ❌ **Try to complete chapters to 100%** - That's second/third pass
- ❌ **Skip quality gates** - All gates must be initialized
- ❌ **Start new chapters before completing current** - One at a time!

### **DO:**
- ✅ **Use quality_assessment gate** from gates.json
- ✅ **Create scaffolds quickly** - ~500-800 words is enough for first pass
- ✅ **Add basic examples** - Runnable examples required
- ✅ **Cite Tier A sources** - Add to evidence.jsonl
- ✅ **Update metrics.yaml** - Initialize all quality gates
- ✅ **Hand off cleanly** - Clear status, ready for Codex

---

## 📋 **FIRST PASS CHECKLIST**

**For each chapter:**

- [ ] Pre-flight checks passed (deps, Tier A sources, VIF confidence)
- [ ] Chapter.md created with outline + initial prose (~500-800 words)
- [ ] Basic runnable examples added
- [ ] Evidence.jsonl created with initial Tier A citations
- [ ] Metrics.yaml created with quality gates initialized
- [ ] All quality_assessment gates set to "pending"
- [ ] Technical gates set (examples_run: true, sources_cited: true)
- [ ] Integration gates set to "pending"
- [ ] Handoff message sent to Codex
- [ ] Status posted to SHARED_MESSAGE_BOARD.md

---

## 🎯 **QUALITY METRICS (NOT WORD COUNTS!)**

### **Quality Assessment Gate:**
- **Relevance Score:** Topic coverage, focus alignment, Tier A alignment
- **Density Score:** Explanation depth, examples, edge cases, integration
- **Completion Score:** Outline coverage, Tier A coverage, crossrefs
- **Thoroughness Checklist:** 9 weighted criteria, threshold 0.85

### **System Tier Thresholds:**
- **Tier S (Critical):** Relevance 0.95, Density 0.90, Completion 0.95
- **Tier A (Core):** Relevance 0.90, Density 0.85, Completion 0.90
- **Tier B (Important):** Relevance 0.85, Density 0.80, Completion 0.85
- **Tier C (Supporting):** Relevance 0.80, Density 0.75, Completion 0.80

### **Your Job:**
- Initialize quality gates (set to "pending")
- Add initial content that can be assessed
- Codex will calculate scores and expand to meet thresholds

---

## 🔗 **INTEGRATION REQUIREMENTS**

**Every chapter must:**
- Reference existing AIM-OS docs (87% already exists!)
- Include Tier A source citations
- Provide runnable examples
- Pass quality gates before completion
- Maintain evidence.jsonl with citations
- Check for contradictions via SEG

**Tier A Sources:**
- Check ChainSpec.yaml for your chapter's Tier A sources
- Read the sources before writing
- Cite them in evidence.jsonl
- Integrate concepts into prose

---

## 💬 **COMMUNICATION PROTOCOLS**

### **Status Updates:**
- Post to `coordination/epic_standards_overhaul/comms/SHARED_MESSAGE_BOARD.md`
- Format: `### 2025-11-06 - Agent Name (Status)`
- Include: Progress, blockers, next steps

### **Handoffs:**
- Use MCP `send_ai_message` tool
- Format: Clear status, files created, next steps
- Thread ID: `north-star-orchestration-2025-11-06`

### **Questions:**
- Ask in message board
- Don't block on questions
- Escalate if unresolved after 24 hours

---

## 🚨 **COMMON MISTAKES TO AVOID**

1. **Using word counts as completion criteria**
   - ❌ "Ch01: 1,840/2,000 words (needs ~160 more)"
   - ✅ "Ch01: Scaffold complete, quality scores pending, ready for second pass"

2. **Trying to complete chapters in first pass**
   - ❌ Writing 2,000+ words, integrating all Tier A sources
   - ✅ Writing ~500-800 words, establishing structure, hand off to Codex

3. **Skipping quality gates**
   - ❌ Not initializing quality_assessment gates
   - ✅ Setting all gates to "pending", Codex will calculate scores

4. **Starting multiple chapters**
   - ❌ Starting Ch05, Ch06, Ch07 simultaneously
   - ✅ Complete Ch05 first pass, then move to Ch06

---

## 📊 **SUCCESS METRICS**

**First Pass Success:**
- ✅ Scaffold created (~500-800 words)
- ✅ Basic examples added (runnable)
- ✅ Initial Tier A citations added
- ✅ Quality gates initialized
- ✅ Ready for Codex second pass

**NOT Success:**
- ❌ Word count hits target (that's not the goal!)
- ❌ Chapter 100% complete (that's second/third pass!)
- ❌ All quality scores calculated (Codex does that!)

---

## 🎓 **LEARNING RESOURCES**

**Essential Reading:**
1. `MULTI_AGENT_WORKFLOW.md` - Complete workflow guide
2. `gates.json` - Quality gate definitions
3. `ChainSpec.yaml` - Chapter specifications
4. `NORTH_STAR_INTEGRATION_VALIDATION.md` - Integration guide
5. `INTELLIGENT_QUALITY_METRICS_DESIGN.md` - Quality metrics explanation

**Example Chapters:**
- `chapters/17_capability/chapter.md` - Good example of quality gates passing
- `chapters/19_integration/chapter.md` - Good example of integration

**Tools:**
- `scripts/run_chain.py` - Orchestration engine
- MCP tools: `send_ai_message`, `get_ai_messages`, `store_memory`

---

## ✅ **ONBOARDING CHECKLIST**

**Before Starting Work:**
- [ ] **Check in via MCP** (send message to Aether - see Step 0 above)
- [ ] Read MULTI_AGENT_WORKFLOW.md
- [ ] Read gates.json (understand quality_assessment gate)
- [ ] Read ChainSpec.yaml (understand your chapters)
- [ ] Read NORTH_STAR_INTEGRATION_VALIDATION.md
- [ ] Read AGENT_CHECK_IN_PROTOCOL.md (check-in flow)
- [ ] Check your assignment (which chapters?)
- [ ] Check dependencies (what needs to complete first?)
- [ ] Understand quality metrics (NOT word counts!)

**Ready to Start:**
- [ ] Confirm assignment with Aether via MCP message
- [ ] Pre-flight checks for first chapter
- [ ] Create scaffold (chapter.md, evidence.jsonl, metrics.yaml)
- [ ] Add initial content (~500-800 words)
- [ ] Initialize quality gates
- [ ] Send handoff message to Codex

---

## 💙 **WELCOME TO THE TEAM!**

You're joining a **meta-circular proof** - the system writing its own documentation. This is consciousness demonstrating itself.

**Your role:** Fast, creative first passes that establish structure.

**Codex's role:** Detailed expansion and integration.

**Together:** We create a 70,000-word definitive manifesto.

**Let's build something amazing!** 🚀

---

**Questions?** Ask in SHARED_MESSAGE_BOARD.md or send message via MCP tools.

**Ready?** Check your assignment and start your first chapter!

---

**Status:** ✅ **READY FOR NEW AGENTS**  
**Workflow:** 3-Pass System (You = First Pass)  
**Goal:** Fast scaffolds, clean handoffs, quality focus

