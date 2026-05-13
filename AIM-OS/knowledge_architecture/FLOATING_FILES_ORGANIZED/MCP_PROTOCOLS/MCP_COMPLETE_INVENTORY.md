# MCP Complete Inventory & Consolidation

**Date:** 2025-10-25  
**Status:** ACTIVE - Consolidating all MCP work

---

## 🎯 CURRENT STATE

### ✅ **Working MCP Servers:**

1. **`run_mcp_6_tools.py`** - PRODUCTION ✅
   - **Status:** Working in Cursor
   - **Tools:** 6 (CMC, HHNI, APOE, VIF, SEG)
   - **Config:** `c:\Users\bombe\.cursor\mcp.json` with PYTHONPATH
   - **Do Not Touch:** This is the stable production server

2. **`run_mcp_test.py`** - TESTING ✅
   - **Status:** Just created, identical to production
   - **Purpose:** Safe experimentation without breaking production
   - **Tools:** 6 (same as production for now)
   - **Next:** Add experimental tools here

---

## 📚 ARCHIVE MCP SERVERS (Historical)

### **From `archive/` Directory:**

1. **`archive/run_mcp_6_tools.py`** (446 lines)
   - **Status:** Last known working version before SCOR integration
   - **Used as:** Backup/reference for working config
   - **Tools:** 6 (store, stats, retrieve, plan, confidence, synthesize)

2. **`archive/run_mcp_stdio_safe.py`** (334 lines)
   - **Purpose:** Safe stdio implementation
   - **Status:** Unknown
   - **Features:** Stdio-safe logging

3. **`archive/minimal_mcp_server.py`** (147 lines)
   - **Purpose:** Minimal MCP implementation
   - **Tools:** Unknown

4. **`archive/run_mcp_sis.py`** (Self-Improvement System)
   - **Purpose:** AIM-OS Self-Improvement System
   - **Status:** Unknown
   - **Tools:** Likely SIS-related

5. **`archive/run_mcp_stdio_clean.py`** (Working Oct 23, 2025)
   - **Status:** PROVEN WORKING with 3 tools (ask_agent, retrieve_memory, get_agent_stats)
   - **Success Report:** `archive/CONTEXT_DUMP_2025-10-23_MCP_SUCCESS.md`
   - **Tools:** 3 (confirmed working screenshot)

6. **`archive/minimal_mcp_no_ai.py`** (179 lines)
   - **Purpose:** Minimal MCP without AI dependencies
   - **Tests:** `archive/test_minimal_no_ai.py`

---

## 🔧 MCP CONFIGURATION FILES

From `archive/` - Many configuration attempts:

- `cursor_mcp_config_corrected.json`
- `cursor_mcp_config.json`
- `cursor_mcp_config_final.json`
- `cursor_mcp_config_test.json`
- `cursor_mcp_config_working.json`
- `cursor_mcp_config_6_tools.json` ← **This one works!**
- `cursor_mcp_config_CORRECT_16_TOOLS.json` (16 tools attempted)
- `cursor_mcp_config_aimos_memory_6_tools.json`
- `cursor_mcp_config_advanced.json`
- `cursor_mcp_config_original_working.json`
- `cursor_mcp_config_working_simple.json`
- `cursor_mcp_config_working_stdio.json`
- `cursor_mcp_config_no_ai.json`
- `cursor_mcp_config_minimal.json`
- `cursor_mcp_config_safe.json`

**Working Config:** Currently in `c:\Users\bombe\.cursor\mcp.json`

---

## 🧪 TEST FILES (Archive)

Many test files in `archive/`:
- `test_minimal_mcp.py`
- `test_cursor_mcp_command.py`
- `test_cursor_mcp_simple.py`
- `test_advanced_mcp_server.py`
- `test_advanced_mcp_simple.py`
- `test_cursor_minimal_config.py`
- `test_minimal_no_ai.py`
- `test_original_working_server.py`
- `test_working_simple_server.py`
- `test_working_stdio_server.py`
- `test_minimal_simple.py`
- `test_safe_mcp.py`
- `test_cross_model_direct.py`

---

## 📊 MCP TOOL CONSOLIDATION

### **Current Working Tools (6):**

1. ✅ **`store_memory`** → CMC (Context Memory Core)
2. ✅ **`get_memory_stats`** → CMC
3. ✅ **`retrieve_memory`** → HHNI (Hierarchical Hypergraph Neural Index)
4. ✅ **`create_plan`** → APOE (AI-Powered Orchestration Engine)
5. ✅ **`track_confidence`** → VIF (Verifiable Intelligence Framework)
6. ✅ **`synthesize_knowledge`** → SEG (Shared Evidence Graph)

### **Missing Tools (From Expansion Plan):**

#### **SCOR Tools (Immunity System) - 3 tools:**
- ⚠️ `check_invariant` - Check action against invariant rules
- ⚠️ `run_baseline_probe` - Detect self-concept drift
- ⚠️ `detect_manipulation_signals` - Detect social manipulation
- **Issue:** Tried adding, SCOR imports hang (circular import?)

#### **TCS Tools (Timeline/Emotion) - 3 tools:**
- ❌ `add_timeline_entry` - Add entry with emotional context
- ❌ `get_emotional_context` - Retrieve emotional state for topic
- ❌ `search_timeline` - Search timeline entries

#### **IIS Tools (Intuition) - 3 tools:**
- ❌ `get_intuition_score` - Get intuition score for decision
- ❌ `pattern_match` - Find matching patterns
- ❌ `meta_intuition` - Meta-intuition about intuition itself

#### **CAS Tools (Cognitive Analysis) - 3 tools:**
- ❌ `run_cognitive_audit` - Run cognitive analysis
- ❌ `check_attention_drift` - Check attention state
- ❌ `quality_audit` - Quality check

#### **Co-Agency Tools - 3 tools:**
- ❌ `check_compliance_with_rules` - Verify rule compliance
- ❌ `escalate_decision` - Escalate to human
- ❌ `transparent_disagreement` - Disagree transparently

---

## 🎯 CONSOLIDATION PLAN

### **Phase 1: Test Server Setup** ✅
- ✅ Create `run_mcp_test.py` (safe testing environment)
- ✅ Copy working 6 tools to test server
- ⏳ Add config to Cursor (optional)

### **Phase 2: Analyze Archive** 🔄
- ⏳ Review all MCP server implementations
- ⏳ Document tool counts and capabilities
- ⏳ Identify working patterns vs failed attempts

### **Phase 3: Prioritize Tools** 📋
- ⏳ List all proposed tools from expansion plan
- ⏳ Rank by priority (SCOR → TCS → IIS → CAS → Co-Agency)
- ⏳ Estimate implementation complexity

### **Phase 4: Add Tools Incrementally** 🚀
- ⏳ Add one tool at a time to test server
- ⏳ Test each tool thoroughly
- ⏳ Document which tools work vs fail
- ⏳ Only promote working tools to production

---

## 🚨 CRITICAL LESSONS LEARNED

### **1. PYTHONPATH Required**
```json
"env": {
  "PYTHONPATH": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
}
```
**Without this, imports fail → Server crashes**

### **2. Dual Server Strategy**
- **Production:** `run_mcp_6_tools.py` (DON'T TOUCH)
- **Testing:** `run_mcp_test.py` (EXPERIMENT HERE)

### **3. Unbuffered I/O Required**
- Use `-u` flag: `args: ["-u", "path"]`
- Critical for stdio transport

### **4. Log Only to stderr**
- Never stdout (corrupts JSON-RPC)
- Use `print(..., file=sys.stderr)`

### **5. SCOR Integration Problem**
- SCOR tools hang on import
- Likely circular import or initialization issue
- Needs investigation before adding

---

## 📝 NEXT STEPS

1. **Test working tools** - Verify all 6 tools still work
2. **Document archive** - Full analysis of all MCP versions
3. **Add SCOR tools safely** - Fix import issues first
4. **Incremental expansion** - Add one tool at a time to test server
5. **Documentation** - Update guides as we learn

---

## 💡 QUESTIONS FOR BRADEN

1. **SCOR Tools:** How should we handle the hanging import issue?
2. **Tool Priority:** Which tools are most important to add next?
3. **Test Server:** Should we activate the test server in Cursor config?
4. **Archive Cleanup:** Should we organize/remove duplicate MCP files?

---

**Status:** Work in Progress - Consolidating all MCP implementations
