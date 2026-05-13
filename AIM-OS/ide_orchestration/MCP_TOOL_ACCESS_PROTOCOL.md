# MCP Tool Access Protocol - Manual Access When MCP Server Not Running

**Date:** 2025-11-19
**Status:** 🔴 **CRITICAL - UNDERSTANDING HOW TO ACCESS MCP DATA**
**User Statement:** "we already consolidated mcp tools and are manual organization protocols for cursor IDE..we need ot also perhaps ensure you are manually adding to and reading mcp tool data even when no mcp tools exist..lets think about this as there seems ot be a lot fo confusion when we are not using mcp tools, or conflicitng what to do...when mcp tools dont need the actual mcp server to run to access them and write them...you cna do it still with tools here."

---

## 🚨 **THE KEY INSIGHT**

**MCP tools don't require the MCP server to be running!**

I can access MCP tool data in THREE ways:

1. **Via Command Server HTTP** - `POST http://localhost:5001/mcp/execute`
2. **Direct Python calls** - Import and call MCP functions directly
3. **Direct data store access** - Access CMC, TCS, HHNI directly

**The confusion:** I've been thinking "MCP tools not available" means I can't use the protocols. But I can ALWAYS use the protocols by accessing the underlying data stores.

---

## 🔧 **THREE WAYS TO ACCESS MCP TOOL DATA**

### **Method 1: Command Server HTTP (When Cursor Extension Running)**

```python
# Via HTTP POST to Command Server
import requests

response = requests.post(
    "http://localhost:5001/mcp/execute",
    json={
        "tool": "store_memory",
        "arguments": {
            "content": "IDE consolidation progress",
            "tags": {"type": "progress", "task": "ide_consolidation"}
        }
    }
)
```

**When to use:** Cursor extension is running, Command Server is available on port 5001

---

### **Method 2: Direct Python Function Calls (Always Available)**

```python
# Import MCP server and call functions directly
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from lucid_mcp_server import SimpleMCPServer

# Initialize server (or just call the functions)
server = SimpleMCPServer()

# Call MCP functions directly
result = server.store_memory({
    "content": "IDE consolidation progress",
    "tags": {"type": "progress", "task": "ide_consolidation"}
})

result = server.add_timeline_entry({
    "prompt_id": "ide_consolidation_001",
    "user_input": "Consolidate all IDEs",
    "context_state": {"phase": "discovery"}
})

result = server.query_goal_timeline({
    "status": "in_progress",
    "limit": 10
})
```

**When to use:** Always available - I can import and call MCP functions directly in Python

---

### **Method 3: Direct Data Store Access (Lowest Level)**

```python
# Access CMC, TCS, HHNI directly
from cmc_service import MemoryStore
from packages.timeline_context_system.tracker import TimelineTracker
from packages.hhni import HierarchicalIndex

# Initialize data stores
memory = MemoryStore("./aimos_memory")
tracker = TimelineTracker()
hhni = HierarchicalIndex()

# Store memory directly in CMC
from cmc_service.models import AtomCreate, AtomContent
atom = memory.create_atom(AtomCreate(
    modality="text",
    content=AtomContent(inline="IDE consolidation progress"),
    tags={"type": "progress", "task": "ide_consolidation"}
))

# Add timeline entry directly
tracker.add_entry(
    prompt_id="ide_consolidation_001",
    user_input="Consolidate all IDEs",
    context_state={"phase": "discovery"}
)

# Query HHNI directly
results = hhni.query("IDE consolidation", limit=10)
```

**When to use:** When I need direct access to data stores, bypassing MCP layer

---

## 📋 **WHAT I SHOULD DO**

### **Always Use Protocols, Regardless of MCP Server Status**

**Instead of:**
- ❌ "MCP tools not available, can't use protocols"
- ❌ "Waiting for MCP server to start"
- ❌ "Can't track progress without MCP tools"

**I should:**
- ✅ Use Command Server HTTP if available
- ✅ Use direct Python function calls if HTTP not available
- ✅ Use direct data store access as fallback
- ✅ ALWAYS follow protocols regardless of MCP server status

---

### **For IDE Consolidation Specifically**

**I should:**

1. **Use `create_plan`** - Via HTTP or direct Python call
   ```python
   # Try HTTP first
   try:
       response = requests.post("http://localhost:5001/mcp/execute", json={
           "tool": "create_plan",
           "arguments": {"goal": "Consolidate all IDEs", "context": "..."}
       })
   except:
       # Fallback to direct Python call
       from lucid_mcp_server import SimpleMCPServer
       server = SimpleMCPServer()
       result = server.create_plan({"goal": "Consolidate all IDEs", "context": "..."})
   ```

2. **Use `add_timeline_entry`** - Track context
   ```python
   # Always track context, regardless of MCP server status
   server.add_timeline_entry({
       "prompt_id": f"ide_consolidation_{timestamp}",
       "user_input": "Consolidate all IDEs",
       "context_state": {"phase": "discovery", "scope": "all_ides"}
   })
   ```

3. **Use `update_goal_progress`** - Track progress
   ```python
   # Update progress as phases complete
   server.update_goal_progress({
       "goal_id": "OBJ-12",
       "progress": 0.25,
       "milestone": "Panel inventory complete"
   })
   ```

4. **Use `query_goal_timeline`** - Check alignment
   ```python
   # Check goal alignment before starting
   goals = server.query_goal_timeline({"status": "in_progress"})
   # Validate IDE consolidation serves OBJ-12
   ```

---

## 🎯 **CONSOLIDATED PROTOCOLS (Already Created)**

**User mentioned:** "we already consolidated mcp tools and are manual organization protocols for cursor IDE"

I need to find:
1. Where are the consolidated MCP tools protocols?
2. Where are the manual organization protocols?
3. How do they work together?

**Searching for:**
- Consolidated MCP tools documentation
- Manual organization protocols
- Cursor IDE specific protocols

---

## 📋 **IMMEDIATE ACTIONS**

1. ✅ **Find consolidated MCP tools protocols** - Search for existing documentation
2. ✅ **Find manual organization protocols** - Search for Cursor IDE protocols
3. ✅ **Understand hybrid approach** - How to use both together
4. ✅ **Implement proper access** - Use HTTP, Python, or direct access as appropriate
5. ✅ **Always follow protocols** - Regardless of MCP server status

---

**Status:** 🔴 **UNDERSTANDING MCP TOOL ACCESS**  
**Created:** 2025-11-19  
**Purpose:** Understand how to access MCP tool data even when MCP server not running

