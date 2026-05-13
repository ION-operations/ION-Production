# MCP Server Restoration Plan - CORRECTED

**Date:** 2025-10-25  
**Status:** ✅ FOUND BOTH VERSIONS  
**Files:** 
- `run_mcp_stdio_clean.py` (3-tool baseline)
- `run_mcp_6_tools.py` (6-tool with CMC)

---

## ✅ **CORRECTED UNDERSTANDING**

### **What You Taught Me:**
- ✅ You HAD a 6-tool version that worked
- ✅ It had MORE tools than the basic 3-tool stdio version
- ✅ You lost it somehow (likely overwritten)
- ✅ It's modular, so can be rebuilt

### **What We Have:**

#### **Version 1: 3-Tool Stdio (Baseline)**
- **File:** `archive/run_mcp_stdio_clean.py`
- **Tools:** `ask_agent`, `retrieve_memory`, `get_agent_stats`
- **Status:** ✅ Documented as working Oct 23
- **Proof:** Context dump confirms

#### **Version 2: 6-Tool MCP (AIM-OS Tools)**
- **File:** `run_mcp_6_tools.py` (in root now!)
- **Tools:**
  1. `store_memory` - Store in CMC
  2. `get_memory_stats` - CMC stats
  3. `retrieve_memory` - Search CMC
  4. `create_plan` - APOE plans
  5. `track_confidence` - VIF tracking
  6. `synthesize_knowledge` - SEG synthesis
- **Status:** File exists, needs testing
- **Note:** This matches your screenshot tools!

---

## 🎯 **RESTORATION STRATEGY**

### **Option A: Start with 3-tool (safer)**
1. Copy `archive/run_mcp_stdio_clean.py` to root
2. Test it works (baseline confirmed working)
3. Build up to 6 tools gradually

### **Option B: Test 6-tool directly**
1. `run_mcp_6_tools.py` already in root
2. Test if it works
3. If broken, debug and fix

### **My Recommendation:**
**Try Option B first** - File already exists, tools match screenshot.  
If it doesn't work, fall back to 3-tool baseline.

---

## 🔍 **KEY INSIGHT YOU PROVIDED**

### **What You Said:**
> "we did have a 6 tool version working with more tools than the basic 3"

**Critical Understanding:**
- ❌ I was wrong: 6-tool version DID exist
- ✅ You're right: It was working with MORE tools
- ✅ Modular: Built on AIM-OS foundations (CMC, APOE, VIF, SEG)
- ✅ Lost: Somehow got overwritten/broken

### **What This Means:**
The 6 tools are AIM-OS native:
- CMC for storage
- APOE for planning
- VIF for tracking
- SEG for synthesis

**Not "random tools"** - These are CORE AIM-OS capabilities exposed via MCP!

---

## 🚀 **TESTING PLAN**

### **Test 1: Does 6-tool server start?**
```powershell
python -u run_mcp_6_tools.py
# Send test: {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
```

### **Test 2: Can we call store_memory?**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "store_memory",
    "arguments": {
      "content": "Test from 6-tool server",
      "tags": {"test": true}
    }
  }
}
```

### **Test 3: Cursor integration**
- Copy to Cursor config
- Restart Cursor
- Test `@aimos store_memory` in chat

---

## 📋 **MODULAR ARCHITECTURE**

### **Why This Should Work:**
Since AIM-OS is modular:
- ✅ CMC service exists
- ✅ APOE exists  
- ✅ VIF exists
- ✅ SEG exists
- ✅ Just need to wire them to MCP

### **If It Doesn't Work:**
Likely issues:
1. Import paths (packages changed)
2. API changes (CMC interface evolved)
3. Dependencies (missing packages)

**All fixable** because architecture is modular!

---

## 💡 **PROVENANCE LESSON**

### **What I Learned:**
1. Your testimony > commit messages
2. You remember the 6-tool version working
3. Screenshot shows `store_memory` and `track_confidence`
4. File exists with those exact tools
5. Modular architecture = rebuildable

### **Correction:**
- ❌ I was wrong: "6-tool version never worked"
- ✅ Reality: "6-tool version existed and worked, then got lost"
- ✅ Solution: Test the existing file, rebuild if needed

---

## 🎯 **NEXT STEP**

**Let's test the 6-tool server:**
1. Check if it imports properly
2. Test `tools/list` call
3. Verify each tool can be called
4. If working → Use it!
5. If broken → Debug or fall back to 3-tool

**Should I start testing it now?**

---

**Status:** Corrected understanding - 6-tool version DID exist  
**Confidence:** Medium (file exists, needs testing)  
**Approach:** Test before claiming success  
**Lesson:** Your memory > my assumptions
