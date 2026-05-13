# MCP Tools Analysis - Ready to Add

**Date:** 2025-10-25  
**Status:** Analyzing what's ready for MCP integration

---

## 🎯 SYSTEMS WITH IMPLEMENTED CODE

### ✅ **SCOR (Sanity Core)** - READY
**Location:** `packages/scor/`  
**Interface:** `SCORInterface` in `scor/interface.py`  
**Status:** Fully implemented, all components ready

**Available Tools:**
1. ✅ `check_invariant` - Check action against invariant rules
2. ✅ `run_baseline_probe` - Detect self-concept drift
3. ✅ `detect_manipulation_signals` - Detect social manipulation in input

**Complexity:** Low (already has clean interface)  
**Previous Issue:** Import hang (needs investigation)  
**Priority:** HIGH (critical safety system)

---

### ✅ **IIS (Intuitive Intelligence System)** - READY
**Location:** `packages/intuitive_intelligence_system/`  
**Interface:** `IntuitionEngine` in `intuition_engine.py`  
**Status:** Implemented with methods

**Available Methods:**
- `compute_intuition_score()` - Get intuition score
- `get_pattern_matches()` - Find matching patterns
- `meta_intuition()` - Meta-intuition about intuition

**Potential Tools:**
1. `get_intuition_score` - Get I(x) score for decision
2. `find_patterns` - Pattern matching for context
3. `meta_analysis` - Analyze intuition quality itself

**Complexity:** Medium (needs wrapper)  
**Priority:** HIGH (valuable capability)

---

### ✅ **TCS (Timeline Context System)** - READY
**Location:** `packages/timeline_context_system/`  
**Interface:** `EnhancedTimelineTracker` in `enhanced_timeline_tracker.py`  
**Status:** Implemented with audit trails

**Available Methods:**
- `add_timeline_node()` - Add entry with emotional context
- `get_emotional_context()` - Retrieve emotional state
- `search_timeline()` - Search timeline entries

**Potential Tools:**
1. `add_timeline_entry` - Add entry with emotional context
2. `get_emotional_context` - Retrieve emotional state for topic
3. `search_timeline` - Search timeline by content/emotion

**Complexity:** Low (straightforward methods)  
**Priority:** MEDIUM (useful but not critical)

---

### ⚠️ **CAS (Cognitive Analysis System)** - DOCUMENTED ONLY
**Location:** `knowledge_architecture/systems/cognitive_analysis/`  
**Status:** Documentation complete, no implementation yet

**Proposed Methods:**
- `run_cognitive_audit()` - Run cognitive analysis
- `check_attention_drift()` - Check attention state
- `quality_audit()` - Quality check

**Complexity:** HIGH (needs implementation first)  
**Priority:** MEDIUM (documentation exists, not implemented)

---

## 📊 READINESS ANALYSIS

### **Tier 1: Ready to Add NOW (Easy)**
1. ✅ **SCOR tools** (if import issue fixed)
   - 3 tools ready
   - Clean interface exists
   - Need to debug import hang

2. ✅ **TCS tools**
   - 3 tools ready
   - Simple wrapper needed
   - No major issues expected

### **Tier 2: Need Wrapper (Medium)**
3. ⚠️ **IIS tools**
   - Methods exist but need MCP wrapper
   - Some integration complexity
   - Should work

### **Tier 3: Not Ready (Needs Implementation)**
4. ❌ **CAS tools**
   - Documentation only
   - No implementation yet
   - Low priority for now

---

## 🚀 RECOMMENDED ADDITION ORDER

### **Phase 1: Easy Wins**
1. **TCS Timeline Tools** (3 tools)
   - `add_timeline_entry`
   - `get_emotional_context`
   - `search_timeline`
   - **Reason:** Simple, no import issues expected
   - **Time:** ~30 minutes

2. **Fix SCOR Import Issue** (investigation)
   - Debug why imports hang
   - Fix circular dependency
   - **Reason:** Critical safety system
   - **Time:** ~1 hour investigation

### **Phase 2: Medium Complexity**
3. **IIS Intuition Tools** (3 tools)
   - `get_intuition_score`
   - `find_patterns`
   - `meta_analysis`
   - **Reason:** Valuable, needs wrapper
   - **Time:** ~1 hour

### **Phase 3: Future**
4. **CAS Tools** (when implemented)
   - Needs full implementation first
   - Not priority for now

---

## 💡 QUICK WINS TO START

**Best First Addition:** TCS Timeline Tools

**Why:**
- Simple interface
- No import issues
- Useful for emotional continuity
- Quick to implement (30 min)
- Low risk

**What It Enables:**
- Track emotional context across sessions
- Search timeline for past emotional states
- Maintain continuity better

---

**Next Step:** Add TCS tools to test server as proof of concept? 🚀
