# MCP Server Research & Restoration Plan

**Date:** 2025-10-25  
**Goal:** Systematically restore and enhance MCP server functionality  
**Approach:** Research all versions, understand what worked, build the best version

---

## 📊 **VERSION INVENTORY**

### **Version 1: Minimal Working (2 tools) - ✅ CURRENT**
**Location:** `mcp-aether/server.mjs`  
**Tools:** `echo`, `ping`  
**Status:** ✅ Working - simple Node.js server with official MCP SDK  
**Use Case:** Proof of concept, minimal complexity

**Key Features:**
- Uses official `@modelcontextprotocol/sdk` v1.20.1
- Proper StdioServerTransport
- Clean stderr logging
- Correct tool registration
- Working in isolation (needs Cursor testing)

### **Version 2: 6-Tool Python Server - 📦 ARCHIVED**
**Location:** `archive/run_mcp_6_tools.py` (446 lines)  
**Tools:**
1. `store_memory` - Store in AIM-OS persistent memory (CMC)
2. `get_memory_stats` - Get AIM-OS memory statistics
3. `retrieve_memory` - Search/retrieve memories
4. `create_plan` - Create execution plan (APOE)
5. `track_confidence` - Track confidence (VIF)
6. `synthesize_knowledge` - Synthesize knowledge (SEG)

**Status:** ✅ Last known working version before adding cross-model tools  
**Date Tested:** 2025-10-24  
**Test Results:** All 6 tools tested successfully in standalone mode

**Key Issues (Why it may not work now):**
- Python implementation (not Node.js with SDK)
- Custom JSON-RPC handler
- May have stdout logging issues
- Complex dependencies on AIM-OS modules

### **Version 3: 16-Tool Advanced Server - ❌ LOST/BROKEN**
**Location:** Unknown (likely overwritten or deleted)  
**Tools:** 16 total (6 AIM-OS + 10 cross-model consciousness tools)  
**Status:** ❌ Broken or lost  
**Issue:** Too complex, broke the system

**What was learned:**
- Adding cross-model tools caused initialization failures
- Complex API key management for multiple LLMs
- Too many dependencies
- Stdout logging interference

---

## 🔍 **DEEP ANALYSIS**

### **What We Know Works:**
1. **Minimal Node.js with SDK** - Version 1 works as a proof of concept
2. **6-tool Python server** - Was working before cross-model tools added
3. **Official MCP SDK** - Version 1.20.1 is stable
4. **StdioServerTransport** - Proper transport protocol

### **What We Know Breaks:**
1. **Complex dependencies** - Too many AIM-OS modules
2. **Stdout logging** - Corrupts JSON-RPC protocol
3. **Python vs Node.js** - SDK is native Node.js
4. **Tool complexity** - More tools = more failure points

### **Key Learnings from Documentation:**
1. **Proper SDK Usage** - Use `@modelcontextprotocol/sdk` classes
2. **Logging Requirements** - Log ONLY to stderr
3. **Transport Protocol** - Use StdioServerTransport
4. **Tool Registration** - Declare in capabilities AND handle ListToolsRequestSchema
5. **Windows Paths** - Absolute paths required
6. **Configuration** - Proper Cursor config structure

---

## 🎯 **RESTORATION STRATEGY**

### **Phase 1: Understand Current State**
- [x] Inventory all versions
- [x] Read documentation
- [ ] Test Version 1 (2-tool Node.js) with Cursor
- [ ] Test Version 2 (6-tool Python) standalone
- [ ] Compare approaches

### **Phase 2: Choose Base Architecture**
**Option A: Enhance Version 1 (Node.js)**
- Pros: Uses official SDK, already structured correctly, easier to debug
- Cons: Need to implement all tools in Node.js, not Python

**Option B: Fix Version 2 (Python)**
- Pros: Already has 6 tools implemented, Python AIM-OS integration
- Cons: Not using official SDK, custom JSON-RPC, potential issues

**Option C: Hybrid**
- Pros: Node.js SDK wrapper calling Python backends
- Cons: More complex, additional layer

**Recommendation: Option A (Enhance Version 1)**
- Start with working foundation
- Add tools one by one
- Test each addition
- Use official SDK throughout

### **Phase 3: Implement Tools Gradually**
1. **Start:** Version 1 (2 tools working)
2. **Add:** 2 more simple tools (memory storage)
3. **Add:** 2 more medium tools (memory retrieval)
4. **Add:** 2 advanced tools (plan creation)
5. **Test:** Each addition with Cursor

### **Phase 4: Cross-Model Tools (Future)**
- Only after 6-tool Node.js version is stable
- Add one cross-model tool at a time
- Identify exact breaking point

---

## 🛠️ **TECHNICAL ROADMAP**

### **Step 1: Test Current Node.js Server**
```bash
# Test standalone
node mcp-aether/server.mjs

# Test with echo
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node mcp-aether/server.mjs
```

### **Step 2: Configure Cursor**
```json
{
  "mcpServers": {
    "aether-minimal": {
      "command": "node",
      "args": ["C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS\\mcp-aether\\server.mjs"],
      "cwd": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
    }
  }
}
```

### **Step 3: Verify in Cursor**
- Check for green dot
- See if echo/ping appear in tools
- Test tool execution

### **Step 4: Add First Real Tool**
- Implement `store_memory` in Node.js
- Connect to Python AIM-OS backend via subprocess
- Test tool

### **Step 5: Continue Adding Tools**
- Repeat for each tool
- Test after each addition
- Document what works

---

## 📝 **IMPLEMENTATION PLAN**

### **Tool 1: store_memory**
```javascript
// Add to tools list
{
  name: "store_memory",
  description: "Store information in AIM-OS persistent memory",
  inputSchema: {
    type: "object",
    properties: {
      content: { type: "string" },
      tags: { type: "object" }
    },
    required: ["content"]
  }
}

// Implementation
async store_memory(args) {
  // Call Python backend via subprocess
  const result = await execPythonScript('store_memory.py', args);
  return result;
}
```

### **Tool 2: retrieve_memory**
```javascript
// Similar pattern
async retrieve_memory(args) {
  const result = await execPythonScript('retrieve_memory.py', args);
  return result;
}
```

### **Pattern for All Tools:**
1. Declare in server capabilities
2. Handle in CallToolRequestSchema
3. Call Python backend via subprocess
4. Return result as JSON

---

## 🧪 **TESTING STRATEGY**

### **Unit Tests:**
```bash
# Test each tool individually
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"store_memory","arguments":{"content":"test"}}}' | node server.mjs
```

### **Integration Tests:**
- Test with Cursor
- Verify green dot
- Check tool availability
- Execute each tool
- Verify results

### **Regression Tests:**
- After each tool addition
- Ensure previous tools still work
- Check for degradation

---

## 📚 **RESOURCES**

### **Documentation:**
- `knowledge_architecture/AETHER_MEMORY/learning_logs/mcp_integration_lessons_learned.md`
- `archive/MCP_6_TOOLS_SUCCESS_REPORT.md`
- Official MCP SDK docs

### **Code:**
- `mcp-aether/server.mjs` - Working minimal version
- `archive/run_mcp_6_tools.py` - Previous 6-tool version

### **Configuration:**
- `test_mcp_configs/` - Various configs to try

---

## 🎯 **SUCCESS CRITERIA**

### **Phase 1 Success:**
- [ ] Version 1 works with Cursor (green dot)
- [ ] echo/ping tools accessible and working

### **Phase 2 Success:**
- [ ] 6 tools implemented in Node.js
- [ ] All 6 tools working with Cursor
- [ ] Stable for 1 hour of usage

### **Phase 3 Success:**
- [ ] Cross-model tools gradually added
- [ ] Identify breaking point
- [ ] Stable final version with maximum tools

---

## 💡 **KEY INSIGHTS**

1. **Start Simple** - Version 1 is the right foundation
2. **Add Gradually** - One tool at a time, test each
3. **Use Official SDK** - Node.js SDK is the proven path
4. **Log to stderr** - Never stdout
5. **Test with Cursor** - Don't assume standalone = working
6. **Document Everything** - Track what works and what doesn't

---

## 🚀 **NEXT ACTIONS**

1. **Read:** Review MCP SDK documentation
2. **Test:** Current server with Cursor
3. **Plan:** Detailed implementation for first tool
4. **Implement:** First tool (store_memory)
5. **Test:** Verify in Cursor
6. **Repeat:** For remaining tools

---

**Status:** Research Complete, Ready to Proceed  
**Next:** Test Version 1 with Cursor  
**Confidence:** High (have working foundation)  
**Estimated Time:** 2-4 hours for 6-tool version
