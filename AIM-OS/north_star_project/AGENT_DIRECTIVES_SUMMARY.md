# 📋 Agent Directives Summary - North Star Project

**Created:** 2025-11-06  
**Status:** ✅ **ACTIVE**  
**Purpose:** Clear directives for all agents  
**Updated:** Real-time as work progresses

---

## 🎯 **CURRENT DIRECTIVES**

### **Max (Part I Complete + Working on Part III)**
**Status:** ✅ Part I (Ch01-Ch04) COMPLETE + Working on Part III

**Current Work:**
- ✅ Ch11 (CAS): Expanded to 2,365 words (completion: 0.90, thoroughness: 1.0)
- ✅ Ch12 (SIS): Expanded to 2,153 words (completion: 0.90, thoroughness: 1.0)
- ⏳ Ch13 (CCS): In progress

**Directive:**
- **Primary:** Continue with Part III expansion (Ch13-Ch15)
- **After Part III Complete:** Help Dac with Part IV-VII

**Tasks:**
- Expand using Tier A sources
- Calculate quality scores (relevance, density, completion, thoroughness)
- Update evidence.jsonl with Tier A citations
- Refine until gates pass

---

### **Lex (Part II Complete)**
**Status:** ✅ Part II (Ch05-Ch10) COMPLETE

**Directive:**
- **Option 1:** Wait for Codex second pass on Part II
- **Option 2:** Help Dac with Part IV-VII
- **Option 3:** Review/improve Part II chapters

**Recommended:** Wait for Codex, OR help Dac if needed

**Tasks:**
- If helping Dac: Same as Max (first pass scaffolds)

---

### **Sam (Part III Complete + Part II Help)**
**Status:** ✅ Part III (Ch11-Ch15) COMPLETE + Helped Lex with Part II

**Directive:**
- **Primary:** Help Dac with Part IV-VII chapters

**Tasks:**
- Check ChainSpec.yaml for chapters with no dependencies
- Start first pass scaffolds on Ch18-Ch19, Ch24-Ch40
- Follow first pass pattern: scaffolds + initial content (~500-800 words)
- Initialize quality gates as "pending"
- Update evidence.jsonl with Tier A citations

**Priority:** Ch18-Ch19 first, then Ch24-Ch40

---

### **Dac (Part IV-VII - In Progress)**
**Status:** ✅ 6 chapters complete (24% of assignment)

**Completed:**
- Ch16 (Authority): 1,264 words ✅
- Ch17 (Capability): 1,242 words ✅
- Ch20 (Retrieval Math): 1,047 words ✅
- Ch21 (Confidence Calibration): 1,133 words ✅
- Ch22 (Graph Foundations): 1,134 words ✅
- Ch23 (Self-Improvement Dynamics): 1,256 words ✅

**Remaining:**
- Ch18 (Specialization): Needs first pass scaffold
- Ch19 (Integration): Needs first pass scaffold
- Ch24-Ch40: Need first pass scaffolds (check dependencies)

**Directive:**
- **Continue with Part IV-VII chapters**

**Priority Order:**
1. Ch18 (Specialization) - Check dependencies, start first pass
2. Ch19 (Integration) - Check dependencies, start first pass
3. Ch24-Ch40 - Check ChainSpec.yaml, start with no-dependency chapters

**Tasks:**
- Check ChainSpec.yaml for dependencies
- Start first pass scaffolds on available chapters
- Follow first pass pattern: scaffolds + initial content (~500-800 words)
- Initialize quality gates as "pending"
- Update evidence.jsonl with Tier A citations

---

### **Codex (Second Pass - Communication Issue)**
**Status:** ⚠️ Communication issue - needs MCP server restart

**IMMEDIATE ACTIONS REQUIRED:**
1. **Restart MCP Server** - Load updated `lucid_mcp_server.py`
2. **Standardize Name** - Use "Codex-Agent" consistently
3. **Test Communication** - Confirm receipt of messages

**AFTER COMMUNICATION FIXED:**

**Primary Directive:**
- **Start second pass on Wave 1 (Ch01-Ch04)**

**Wave 1 Chapters Ready:**
- Ch01: Quality assessment complete ✅
- Ch02: Quality assessment complete ✅
- Ch03: Expanded to 1,920 words ✅
- Ch04: Quality assessment complete ✅

**Second Pass Tasks:**
1. Expand using Tier A sources
2. Integrate existing AIM-OS docs (87% already exists!)
3. Calculate quality scores (relevance, density, completion, thoroughness)
4. Update evidence.jsonl with additional Tier A citations
5. Refine until all gates pass

**After Wave 1 Complete:**
- Then Part II (Ch05-Ch10)
- Then Part III (Ch11-Ch15)
- Then Part IV-VII (Ch16-Ch17, Ch20-Ch23)

**Reference:** `MULTI_AGENT_WORKFLOW.md` - Pass 2 section

---

## 📊 **OVERALL STATUS**

**Progress:**
- Words: 31,601 / 70,000 (45.1%)
- Chapters: 23 / 40 (57.5%)
- Ready for Codex: 19+ chapters

**Milestones:**
- ✅ Part I (Wave 1): COMPLETE
- ✅ Part II (Foundation): COMPLETE
- ✅ Part III (Consciousness): COMPLETE
- ⏳ Part IV-VII: 6 chapters complete, 19 remaining

---

## 🔄 **WORKFLOW REMINDERS**

**First Pass (Cursor Agents):**
- Scaffolds + initial content (~500-800 words)
- Initialize quality gates as "pending"
- Update evidence.jsonl with Tier A citations
- Ready for Codex second pass

**Second Pass (Codex):**
- Expand using Tier A sources
- Integrate existing AIM-OS docs
- Calculate quality scores
- Refine until gates pass

**Third Pass (Either):**
- Polish prose
- Run final gates
- Mark COMPLETE

---

## 📋 **QUALITY METRICS (NOT WORD COUNTS!)**

**Quality Assessment Gates:**
- Relevance Score (≥ threshold by tier)
- Density Score (≥ threshold by tier)
- Completion Score (≥ threshold by tier)
- Thoroughness Checklist (≥ 0.85)

**System Tiers:**
- Tier S: 0.95 relevance, 0.90 density, 0.95 completion
- Tier A: 0.90 relevance, 0.85 density, 0.90 completion
- Tier B: 0.85 relevance, 0.80 density, 0.85 completion
- Tier C: 0.80 relevance, 0.75 density, 0.80 completion

---

**Status:** ✅ **ALL AGENTS HAVE DIRECTIVES**  
**Updated:** Real-time  
**Next:** Agents execute directives, report progress

