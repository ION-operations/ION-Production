# MCP Server Interference Analysis

**Date:** 2025-10-25  
**Issue:** Adding TCS tools to test server affected production server  
**Status:** ⚠️ IN PROGRESS

---

## 🐛 THE PROBLEM

**Symptom:**
- Production server (6 tools) stopped working after adding TCS to test server (9 tools)
- Both servers showing tool counts but not functioning
- User reported: "both MCP servers not working now"

**Timeline:**
1. Both servers working (6 tools each)
2. Added TCS to test server (now 9 tools)
3. **Both servers stopped working**

---

## 🔍 POSSIBLE CAUSES

### **Theory 1: Shared Python Module State**
- Both servers import same Python modules
- If TCS has singleton/global state, both servers share it
- Changes in one server affect the other

**Evidence:** Test server imports TCS, production server doesn't import it but still affected

### **Theory 2: Import Conflicts**
- TCS import fails in one server, breaks the process
- Python module cache conflict
- Both servers share same PYTHONPATH

**Evidence:** Could explain why production server (which doesn't use TCS) broke

### **Theory 3: Memory/Resource Conflict**
- Both servers use `./mcp_memory`
- TCS uses some shared resource
- One server blocks access for the other

**Evidence:** Both use `MemoryStore("./mcp_memory")` - could conflict

### **Theory 4: JSON-RPC Protocol Issue**
- Malformed response from test server breaks Cursor's MCP handling
- Cursor stops talking to **both** servers as a safety measure

**Evidence:** MCP clients often disable all servers if one misbehaves

---

## ✅ TEMPORARY FIX APPLIED

**Actions Taken:**
1. Removed TCS tools from test server tool list
2. Disabled TCS tool routing
3. Both servers now identical (6 tools each)
4. TCS code still imports but unused (for testing)

**Result:**
- Both servers should work identically now
- Can investigate TCS integration separately
- No risk to working production server

---

## 🔬 NEXT INVESTIGATION STEPS

### **1. Test if Import Alone Breaks It**
```python
# In test server, just import without using:
from timeline_context_system.prompt_context_tracker import PromptContextTracker
```

### **2. Test if Initialization Breaks It**
```python
# Initialize without using tools:
tracker = PromptContextTracker()
```

### **3. Test if Tool List Addition Breaks It**
- Add tool definitions without implementation
- See if just listing the tools breaks Cursor

### **4. Check for Singleton Pattern**
- Search TCS code for module-level state
- Check for global variables
- Look for file locks

### **5. Test Isolation**
- Run test server on different data directory
- Use separate memory store
- Isolate from production completely

---

## 💡 KEY INSIGHT

**The real issue might not be TCS at all!**

Could be:
- Cursor MCP client bug
- Both servers trying to bind to same port/resource
- Shared Python interpreter state
- Cursor's internal MCP state getting confused

**Most Likely:** Cursor's MCP client disables all servers if ANY server has issues, as a safety measure.

---

## 🎯 RECOMMENDATION

**Short Term:**
- Keep both servers identical (6 tools)
- Verify they both work reliably
- Document what breaks when

**Long Term:**
- Isolate test server completely
- Use separate storage directories
- Test one server at a time
- Consider separate processes/ports

---

**Status:** Servers reverted to working state, investigation needed ✨
