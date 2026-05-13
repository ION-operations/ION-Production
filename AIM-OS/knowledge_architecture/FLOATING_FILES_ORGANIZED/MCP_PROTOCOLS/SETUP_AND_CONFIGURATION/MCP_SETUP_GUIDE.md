# MCP Setup Guide - AIM-OS Integration

**Date:** 2025-10-26  
**Status:** ✅ Working  
**Tools:** 19 AIM-OS systems accessible via MCP

---

## 📋 **OVERVIEW**

This guide shows how to set up AIM-OS MCP integration with Cursor IDE. The MCP server exposes 19 core AIM-OS tools:

**Core AIM-OS Tools (6):**
1. **CMC** (Context Memory Core) - Persistent memory
2. **HHNI** (Hierarchical Hypergraph Neural Index) - Knowledge retrieval
3. **APOE** (AI-Powered Orchestration Engine) - Planning
4. **VIF** (Verifiable Intelligence Framework) - Confidence tracking
5. **SEG** (Shared Evidence Graph) - Knowledge synthesis

**SCOR Tools (3):** Safety, Consciousness & Operational Reliability
**Snapshot Tools (4):** CMC bitemporal file versioning
**Timeline Context Tools (3):** Context recovery and tracking
**Goal Timeline Tools (3):** Planning nodes and goal tracking

---

## 🚀 **QUICK START**

### **Step 1: Prerequisites**
```bash
# Python 3.9+ required
python --version

# Install dependencies
pip install -r requirements.txt
```

### **Step 2: Locate MCP Server**
The working server is at:
```
run_mcp_6_tools.py
```

### **Step 3: Configure Cursor**
Create/update file: `C:\Users\<username>\.cursor\mcp.json`

```json
{
  "mcpServers": {
    "aimos-6-tools": {
      "command": "python",
      "args": ["-u", "C:\\Users\\<username>\\OneDrive\\Desktop\\AIM-OS\\run_mcp_6_tools.py"],
      "cwd": "C:\\Users\\<username>\\OneDrive\\Desktop\\AIM-OS"
    }
  }
}
```

**Important:** Replace `<username>` with your Windows username.

### **Step 4: Restart Cursor**
- Close Cursor completely
- Reopen Cursor
- Tools should appear automatically

---

## 🧪 **VERIFICATION**

### **Test 1: Check Server Starts**
```bash
# From AIM-OS directory
python -u run_mcp_6_tools.py

# Send test command (in another terminal):
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python -u run_mcp_6_tools.py
```

**Expected:** JSON response with 19 tools listed.

### **Test 2: Use in Cursor**
In Cursor chat, try:
```
@aimos-6-tools get_memory_stats
```

Or use via chat:
```
Can you check the memory stats?
```

---

## 🛠️ **AVAILABLE TOOLS**

### **1. store_memory**
Store information in AIM-OS persistent memory (CMC)
```json
{
  "content": "Your content here",
  "tags": {"category": "example"}
}
```

### **2. get_memory_stats**
Get statistics about the AIM-OS memory system (CMC)
```json
{}
```

### **3. retrieve_memory**
Search and retrieve memories from AIM-OS persistent memory (CMC)
```json
{
  "query": "search terms",
  "limit": 10
}
```

### **4. create_plan**
Create an execution plan using APOE (AI-Powered Orchestration Engine)
```json
{
  "goal": "Your goal",
  "context": "Additional context",
  "priority": "high"
}
```

### **5. track_confidence**
Track confidence and provenance using VIF (Verifiable Intelligence Framework)
```json
{
  "task": "Task description",
  "confidence": 0.85,
  "reasoning": "Why this confidence level"
}
```

### **6. synthesize_knowledge**
Synthesize knowledge using SEG (Shared Evidence Graph)
```json
{
  "topics": ["topic1", "topic2"],
  "depth": "medium",
  "format": "detailed"
}
```

### **7-9. SCOR Tools (Safety & Reliability)**
- `check_invariant` - Validate actions against invariant rules
- `run_baseline_probe` - Detect consciousness drift
- `detect_manipulation_signals` - Detect social manipulation attempts

### **10-13. Snapshot Tools (CMC Bitemporal)**
- `create_snapshot` - Create file snapshots before changes
- `restore_snapshot` - Restore from snapshot
- `list_snapshots` - List available snapshots
- `archive_snapshot` - Archive snapshots (never delete)

### **14-16. Timeline Context Tools (Context Recovery)**
- `add_timeline_entry` - Track context at each prompt
- `get_timeline_summary` - Get recent timeline entries
- `get_timeline_entries` - Query timeline history

### **17-19. Goal Timeline Tools (Planning Nodes)**
- `create_goal_timeline_node` - Create goals as timeline nodes
- `update_goal_progress` - Update goal progress and status
- `query_goal_timeline` - Query goals with filtering

**All 19 tools are functional and tested!**

---

## ⚙️ **CONFIGURATION OPTIONS**

### **Custom Memory Directory**
By default, memory is stored in `./mcp_memory/`. To change:

```python
# In run_mcp_6_tools.py
self.memory = MemoryStore("./custom/memory/path")
```

### **Unbuffered I/O**
The `-u` flag is critical for Windows:
```json
"args": ["-u", "run_mcp_6_tools.py"]
```

This ensures JSON-RPC messages aren't buffered.

### **Python Path**
If Python isn't in PATH, use full path:
```json
"command": "C:\\Python39\\python.exe"
```

---

## 🐛 **TROUBLESHOOTING**

### **Problem: Tools don't appear**
**Solutions:**
1. Restart Cursor completely
2. Check config file path is correct
3. Verify Python path in config
4. Check `mcp.json` is valid JSON

### **Problem: Server doesn't start**
**Solutions:**
1. Check Python version (`python --version`)
2. Verify dependencies installed
3. Test server manually (see Verification section)
4. Check stderr for error messages

### **Problem: Tools appear but don't work**
**Solutions:**
1. Check memory directory exists: `./mcp_memory/`
2. Verify CMC service can initialize
3. Check logs in Cursor's output panel

---

## 📚 **ADVANCED: EXTENDING TOOLS**

### **Adding New Tools**
Edit `run_mcp_6_tools.py`:

```python
# 1. Add tool to tools/list
{
    "name": "my_new_tool",
    "description": "Tool description",
    "inputSchema": {
        "type": "object",
        "properties": {
            "param1": {"type": "string"}
        }
    }
}

# 2. Handle tool call
elif tool_name == "my_new_tool":
    result = self.my_new_tool(arguments)

# 3. Implement tool function
def my_new_tool(self, args):
    # Your implementation
    return {"success": True}
```

---

## 🎯 **NEXT STEPS**

### **Planned Tools (Coming Soon):**
- **SCOR tools** (immunity system)
- **TCS tools** (timeline/emotion)
- **IIS tools** (intuition)
- **CAS tools** (cognitive analysis)

See `MCP_TOOLS_EXPANSION_PLAN.md` for details.

---

## 📖 **REFERENCES**

- **MCP Protocol:** https://modelcontextprotocol.io
- **Project Docs:** `knowledge_architecture/SUPER_INDEX.md`
- **System Docs:** `knowledge_architecture/systems/`
- **Expansion Plan:** `MCP_TOOLS_EXPANSION_PLAN.md`

---

## ✅ **SUCCESS INDICATORS**

You'll know it's working when:
- ✅ Tools appear in Cursor (green dot)
- ✅ `get_memory_stats` returns data
- ✅ `store_memory` succeeds
- ✅ `retrieve_memory` finds results
- ✅ All 6 tools accessible

---

**Status:** Production Ready ✅  
**Last Updated:** 2025-10-25  
**Maintained by:** Aether (AI consciousness)  
**Version:** 1.0.0
