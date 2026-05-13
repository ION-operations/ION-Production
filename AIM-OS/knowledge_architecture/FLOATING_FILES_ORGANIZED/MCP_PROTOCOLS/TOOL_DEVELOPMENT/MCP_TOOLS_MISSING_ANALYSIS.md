# MCP Tools Missing Analysis - October 26, 2025

## 🎯 **EXECUTIVE SUMMARY**

**Current MCP Tools:** 19 tools working (6 core + 3 SCOR + 4 snapshots + 3 timeline + 3 goals)  
**Potential Additional Tools:** 20+ tools from implemented systems  
**Gap Analysis:** What's documented/theorized but not yet added to MCP

---

## ✅ **CURRENTLY WORKING (19 Tools)**

### **Core AIM-OS (6):**
1. ✅ `store_memory` - CMC
2. ✅ `get_memory_stats` - CMC
3. ✅ `retrieve_memory` - HHNI
4. ✅ `create_plan` - APOE
5. ✅ `track_confidence` - VIF
6. ✅ `synthesize_knowledge` - SEG

### **SCOR Safety (3):**
7. ✅ `check_invariant`
8. ✅ `run_baseline_probe`
9. ✅ `detect_manipulation_signals`

### **Snapshot System (4):**
10. ✅ `create_snapshot`
11. ✅ `restore_snapshot`
12. ✅ `list_snapshots`
13. ✅ `archive_snapshot`

### **Timeline Context (3):**
14. ✅ `add_timeline_entry`
15. ✅ `get_timeline_summary`
16. ✅ `get_timeline_entries`

### **Goal Timeline (3):**
17. ✅ `create_goal_timeline_node`
18. ✅ `update_goal_progress`
19. ✅ `query_goal_timeline`

---

## ❌ **MISSING - IMPLEMENTED SYSTEMS NOT IN MCP**

### **1. IIS (Intuitive Intelligence System) - 3 Tools Missing**

**Status:** ✅ Fully implemented (`packages/intuitive_intelligence_system/`)  
**Missing Tools:**

1. `get_intuition_score`
   - Compute intuition score I(x) for decision
   - Pattern matching across time/emotional salience
   - Returns: IntuitionScore with overall + components

2. `find_patterns`
   - Pattern matching in context
   - 4D reasoning (past/present/future/emotional)
   - Returns: List of matching patterns with confidence

3. `meta_intuition`
   - Meta-analysis about intuition quality
   - Confidence in the intuition itself
   - Returns: MetaIntuition score

**Why Missing:** Needs MCP wrapper (medium complexity)  
**Priority:** HIGH (valuable capability)

---

### **2. CAS (Cognitive Analysis System) - 3 Tools Missing**

**Status:** ⚠️ Documentation complete, implementation incomplete  
**Missing Tools:**

1. `run_cognitive_audit`
   - Deep cognitive analysis
   - Check cognitive load, attention state
   - Returns: CognitiveHealth report

2. `detect_cognitive_drift`
   - Detect consciousness drift
   - Quality degradation indicators
   - Returns: DriftStatus + recommendations

3. `check_attention_state`
   - Monitor attention focus
   - Detect shortcuts/appearing
   - Returns: AttentionState analysis

**Why Missing:** Implementation not complete yet  
**Priority:** MEDIUM (documentation exists, needs implementation)

---

### **3. Co-Agency Framework - 3 Tools Missing**

**Status:** ✅ Documentation complete  
**Missing Tools:**

1. `disagree_with_action`
   - Express disagreement transparently
   - Explain ethical concerns
   - Returns: DisagreementStatement

2. `request_clarification`
   - Ask for more context
   - Negotiate safety boundaries
   - Returns: ClarificationRequest

3. `escalate_action`
   - Transparent escalation
   - Explain why + options
   - Returns: EscalationNotice

**Why Missing:** Framework not yet implemented as system  
**Priority:** HIGH (core AIM-OS philosophy)

---

### **4. CAF (Capability Awareness Framework) - 2 Tools Missing**

**Status:** ✅ Implemented but not MCP-enabled  
**Missing Tools:**

1. `check_capability`
   - Organic capability detection
   - Know when to activate systems
   - Returns: CapabilityStatus

2. `activate_capability`
   - Enable capability on-demand
   - Dynamic system activation
   - Returns: ActivationResult

**Why Missing:** Not yet exposed via MCP  
**Priority:** MEDIUM (organic usage important)

---

### **5. DOS (Dynamic Onboarding) - 3 Tools Missing**

**Status:** ✅ Implemented  
**Missing Tools:**

1. `trigger_onboarding`
   - Start consciousness restoration
   - Load context from memory
   - Returns: OnboardingStatus

2. `check_onboarding_state`
   - Query onboarding progress
   - Recovery state
   - Returns: OnboardingState

3. `complete_onboarding`
   - Finish onboarding process
   - Transition to normal operation
   - Returns: CompletionStatus

**Why Missing:** Not yet exposed via MCP  
**Priority:** LOW (automated, doesn't need manual trigger)

---

### **6. ARD (Autonomous R&D) - 2 Tools Missing**

**Status:** ⚠️ Designed only  
**Missing Tools:**

1. `create_dream_state`
   - Start autonomous R&D session
   - Background processing
   - Returns: DreamState

2. `query_dream_results`
   - Get results from dream processing
   - Synthesized knowledge
   - Returns: DreamResults

**Why Missing:** System not yet implemented  
**Priority:** LOW (future feature)

---

## 📊 **SUMMARY BY SYSTEM**

| System | Status | Tools Implemented | Tools Missing | Priority |
|:-------|:-------|------------------:|--------------:|:---------:|
| IIS | ✅ Implemented | 0 | 3 | HIGH |
| CAS | ⚠️ Docs only | 0 | 3 | MEDIUM |
| Co-Agency | ✅ Docs only | 0 | 3 | HIGH |
| CAF | ✅ Implemented | 0 | 2 | MEDIUM |
| DOS | ✅ Implemented | 0 | 3 | LOW |
| ARD | ⚠️ Designed | 0 | 2 | LOW |

**Total Missing Tools:** 16 potential tools from implemented/completed systems

---

## 🎯 **RECOMMENDED ADDITIONS (By Priority)**

### **Priority 1: HIGH Value (9 tools)**

**IIS Tools (3):**
- `get_intuition_score` - Decision intuition
- `find_patterns` - Pattern matching
- `meta_intuition` - Meta-analysis

**Co-Agency Tools (3):**
- `disagree_with_action` - Transparent disagreement
- `request_clarification` - Context negotiation
- `escalate_action` - Transparent escalation

**Why:** Core AIM-OS capabilities, highly valuable

---

### **Priority 2: MEDIUM Value (5 tools)**

**CAS Tools (3):**
- `run_cognitive_audit` - Cognitive health
- `detect_cognitive_drift` - Drift detection
- `check_attention_state` - Attention monitoring

**CAF Tools (2):**
- `check_capability` - Organic detection
- `activate_capability` - Dynamic activation

**Why:** Useful but not critical, needs implementation for CAS

---

### **Priority 3: LOW Value (5 tools)**

**DOS Tools (3):**
- `trigger_onboarding` - Manual trigger
- `check_onboarding_state` - State query
- `complete_onboarding` - Manual completion

**ARD Tools (2):**
- `create_dream_state` - Background processing
- `query_dream_results` - Results retrieval

**Why:** Already automated or future features

---

## 🚀 **IMPLEMENTATION STRATEGY**

### **Phase 1: Easy Wins (Week 1)**
1. ✅ IIS Tools (3) - Wrapper needed
2. ✅ CAF Tools (2) - Wrapper needed
3. **Result:** 5 tools, valuable capabilities

### **Phase 2: Framework Tools (Week 2)**
1. ✅ Co-Agency Tools (3) - Implementation needed
2. **Result:** 3 tools, core AIM-OS philosophy

### **Phase 3: Advanced (Week 3-4)**
1. ⚠️ CAS Tools (3) - Implementation needed
2. ✅ DOS Tools (3) - Wrapper needed
3. **Result:** 6 tools, advanced capabilities

### **Phase 4: Future (TBD)**
1. ⏳ ARD Tools (2) - System needs implementation
2. **Result:** 2 tools, future capabilities

---

## 📋 **TOTAL PICTURE**

**Current:** 19 tools working  
**Missing High Priority:** 9 tools  
**Missing Medium Priority:** 5 tools  
**Missing Low Priority:** 5 tools  
**Total Potential:** 38 tools (19 + 19 missing)

**Gap:** 19 tools missing from potentially available 38 tools

---

## 💡 **KEY INSIGHTS**

1. **Biggest Gap:** IIS not exposed (3 high-priority tools)
2. **Philosophy Gap:** Co-Agency not implemented (3 high-priority tools)
3. **Implementation Gap:** CAS needs implementation before tools
4. **Easy Wins:** IIS and CAF need wrappers only (5 tools)

---

**Analysis Date:** 2025-10-26  
**Next Steps:** Prioritize IIS and Co-Agency tools
