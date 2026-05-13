# MCP Tools Ready to Add

**Date:** 2025-10-25  
**Status:** Analyzing ready systems

---

## ✅ SYSTEMS READY FOR MCP TOOLS

### **1. SCOR (Sanity Core)** - HIGH PRIORITY
**Status:** Fully implemented  
**Location:** `packages/scor/`  
**Issue:** Import hang (needs investigation)

**Available Tools:**
- `check_invariant` - Check action against invariant rules
- `run_baseline_probe` - Detect self-concept drift  
- `detect_manipulation_signals` - Detect social manipulation

**Action:** Debug import issue first

---

### **2. TCS (Timeline Context System)** - EASY ADD
**Status:** Fully implemented  
**Location:** `packages/timeline_context_system/`  
**Issue:** None known

**Available Tools:**
- `add_timeline_entry` - Add timeline entry with context
- `get_timeline_summary` - Get timeline summary  
- `search_timeline_entries` - Search timeline by content

**Action:** Add to test server (simple wrapper)

---

### **3. IIS (Intuitive Intelligence)** - MEDIUM PRIORITY
**Status:** Implemented  
**Location:** `packages/intuitive_intelligence_system/`  
**Issue:** Needs wrapper

**Available Tools:**
- `get_intuition_score` - Get I(x) score
- `find_patterns` - Pattern matching
- `meta_intuition` - Meta-analysis

**Action:** Add wrapper layer

---

### **4. CAS (Cognitive Analysis)** - NOT READY
**Status:** Documentation only  
**Location:** Documentation  
**Issue:** No implementation

**Action:** Skip for now

---

## 🚀 RECOMMENDED FIRST ADDITION

**TCS Timeline Tools** - Best starting point

**Why:**
- ✅ Fully implemented
- ✅ No known issues
- ✅ Simple methods
- ✅ Useful for continuity
- ✅ Low risk

**Tools to Add:**
1. `add_timeline_entry` - Simple entry addition
2. `get_timeline_summary` - Summary retrieval
3. `get_timeline_for_task` - Task-specific timeline

**Estimated Time:** 30 minutes

---

**Next:** Add TCS tools to test server? 🚀
