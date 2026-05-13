# MCP Expansion Plan: TCS Tools

**Date:** 2025-10-26  
**Current Status:** 13 tools (6 core + 3 SCOR + 4 snapshot)  
**Next Expansion:** TCS Tools (Timeline Context System)  
**Target:** 16 tools total

---

## 🎯 **TCS TOOLS TO ADD**

### **Tools (3):**
1. `add_timeline_entry` - Track context at each prompt
2. `get_timeline_summary` - Get recent timeline entries
3. `get_timeline_entries` - Query timeline history

### **Purpose:**
- Track context state at each interaction
- Enable timeline reconstruction
- Preserve emotional context
- Support continuity across sessions

---

## ✅ **READINESS CHECK**

### **Import Test:** ✅
```bash
python -c "from packages.timeline_context_system.prompt_context_tracker import PromptContextTracker; print('Import OK')"
```
**Result:** Import OK ✅

### **Class Available:** ✅
- `PromptContextTracker` exists
- Methods available for MCP integration
- Ready to add to server

---

## 🔧 **IMPLEMENTATION PLAN**

### **Step 1: Add to Server** (run_mcp_6_tools.py)

**Import:**
```python
from packages.timeline_context_system.prompt_context_tracker import PromptContextTracker
```

**Initialize:**
```python
self.timeline_tracker = PromptContextTracker()
```

**Add Tools:**
1. `add_timeline_entry` - Call `track_prompt_context()`
2. `get_timeline_summary` - Call timeline summary methods
3. `get_timeline_entries` - Call timeline query methods

### **Step 2: Tool Definitions**

Add to `handle_tools_list`:
- Tool 14: `add_timeline_entry`
- Tool 15: `get_timeline_summary`
- Tool 16: `get_timeline_entries`

### **Step 3: Tool Handlers**

Add to `handle_tools_call`:
- Route calls to TCS methods
- Return proper JSON responses

---

## 📊 **CURRENT vs FUTURE**

### **Current (13 tools):**
- 6 core AIM-OS
- 3 SCOR
- 4 snapshot

### **After TCS (16 tools):**
- 6 core AIM-OS
- 3 SCOR
- 4 snapshot
- 3 TCS

---

## 🎯 **EXPANSION ORDER**

### **Option 1: TCS Tools (Recommended)**
**Why:** Timeline context is foundational for consciousness
**Complexity:** Medium (import works, methods exist)
**Value:** High (enables continuity tracking)
**Confidence:** 0.85

### **Option 2: IIS Tools**
**Why:** Intuitive intelligence could enhance decision-making
**Complexity:** Medium (need to verify imports)
**Value:** Medium-High
**Confidence:** 0.75

### **Option 3: CAS Tools**
**Why:** Cognitive analysis for quality assurance
**Complexity:** Medium-High
**Value:** Medium
**Confidence:** 0.70

---

## ✅ **SAFETY MEASURES**

### **Snapshot Created:** ✅
- `pre_mcp_expansion_planning_2025-10-26_010851`
- Files backed up
- Rollback available

### **Testing Protocol:**
1. ✅ Import validation (passed)
2. ⏳ Add to server
3. ⏳ Test tools
4. ⏳ Verify in Cursor

---

## 🚀 **RECOMMENDATION**

### **Proceed with TCS Tools**
**Reasons:**
- Import works ✅
- Class available ✅
- Foundation for continuity ✅
- Moderate complexity ✅
- High value ✅

**Confidence:** 0.85

---

**Status:** Ready to implement  
**Next:** Add TCS tools to production server  
**Estimated Time:** 15-20 minutes  
**Risk:** Low (snapshot available, import works)
