# MCP Manual Access Protocol - Accessing MCP Data Without MCP Server

**Date:** 2025-11-19
**Status:** 🔴 **CRITICAL - IMPLEMENTING NOW**
**User Statement:** "we already consolidated mcp tools and are manual organization protocols for cursor IDE..we need ot also perhaps ensure you are manually adding to and reading mcp tool data even when no mcp tools exist..lets think about this as there seems ot be a lot fo confusion when we are not using mcp tools, or conflicitng what to do...when mcp tools dont need the actual mcp server to run to access them and write them...you cna do it still with tools here."

---

## 🚨 **THE KEY INSIGHT**

**I can access MCP tool data in THREE ways, regardless of MCP server status:**

1. **Command Server HTTP** - `POST http://localhost:5001/mcp/execute` (when Cursor extension running)
2. **Direct Python function calls** - Import `lucid_mcp_server` and call functions directly
3. **Direct data store access** - Access CMC, TCS, HHNI directly via Python imports

**I should ALWAYS use protocols, regardless of MCP server status.**

---

## 🔧 **THREE METHODS TO ACCESS MCP DATA**

### **Method 1: Command Server HTTP (When Available)**

```python
import requests

# Try Command Server HTTP first
try:
    response = requests.post(
        "http://localhost:5001/mcp/execute",
        json={
            "tool": "store_memory",
            "arguments": {
                "content": "IDE consolidation progress",
                "tags": {"type": "progress", "task": "ide_consolidation"}
            }
        },
        timeout=5
    )
    if response.ok:
        result = response.json()
        return result
except:
    # Fallback to Method 2 or 3
    pass
```

**When to use:** Cursor extension is running, Command Server available on port 5001

---

### **Method 2: Direct Python Function Calls (Always Available)**

```python
import sys
from pathlib import Path

# Add workspace to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

# Import and initialize MCP server
from lucid_mcp_server import SimpleMCPServer

# Initialize server (or just call functions)
server = SimpleMCPServer()

# Call MCP functions directly
result = server.store_memory({
    "content": "IDE consolidation progress",
    "tags": {"type": "progress", "task": "ide_consolidation"}
})

result = server.add_timeline_entry({
    "prompt_id": "ide_consolidation_001",
    "user_input": "Consolidate all IDEs",
    "context_state": {"phase": "discovery", "scope": "all_ides"}
})

result = server.query_goal_timeline({
    "status": "in_progress",
    "limit": 10
})

result = server.create_plan({
    "goal": "Consolidate all 6 IDE prototypes + 1 main app = 100+ panels",
    "context": "Discovery phase - reading panel registries, identifying duplicates",
    "priority": "high"
})

result = server.update_goal_progress({
    "goal_id": "OBJ-12",
    "progress": 0.25,
    "milestone": "Panel inventory complete"
})
```

**When to use:** Always available - I can import and call MCP functions directly in Python

---

### **Method 3: Direct Data Store Access (Lowest Level)**

```python
# Access CMC, TCS, HHNI directly
from cmc_service import MemoryStore
from cmc_service.models import AtomCreate, AtomContent
from packages.timeline_context_system.prompt_context_tracker import PromptContextTracker
from packages.timeline_context_system.goal_timeline_node import GoalTimelineNode, GoalStatus
from hhni import HierarchicalIndex

# Initialize data stores
memory = MemoryStore("./aimos_memory")
tracker = PromptContextTracker()

# Store memory directly in CMC
atom = memory.create_atom(AtomCreate(
    modality="text",
    content=AtomContent(inline="IDE consolidation progress"),
    tags={"type": "progress", "task": "ide_consolidation"}
))

# Add timeline entry directly
tracker.add_entry(
    prompt_id="ide_consolidation_001",
    user_input="Consolidate all IDEs",
    context_state={"phase": "discovery", "scope": "all_ides"}
)

# Query HHNI directly
if hhni_index:
    results = hhni_index.query("IDE consolidation", limit=10)
```

**When to use:** When I need direct access to data stores, bypassing MCP layer

---

## 📋 **WHAT I MUST DO FOR IDE CONSOLIDATION**

### **Always Use Protocols, Regardless of MCP Server Status**

**Instead of:**
- ❌ "MCP tools not available, can't use protocols"
- ❌ "Waiting for MCP server to start"
- ❌ "Can't track progress without MCP tools"

**I should:**
- ✅ Try Command Server HTTP first
- ✅ Fallback to direct Python function calls
- ✅ Fallback to direct data store access
- ✅ ALWAYS follow protocols regardless of MCP server status

---

### **Implementation Pattern**

```python
def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """Call MCP tool with fallback chain"""
    
    # Method 1: Try Command Server HTTP
    try:
        response = requests.post(
            "http://localhost:5001/mcp/execute",
            json={"tool": tool_name, "arguments": arguments},
            timeout=5
        )
        if response.ok:
            return response.json()
    except:
        pass
    
    # Method 2: Try direct Python function calls
    try:
        from lucid_mcp_server import SimpleMCPServer
        server = SimpleMCPServer()
        func = getattr(server, tool_name, None)
        if func:
            return func(arguments)
    except:
        pass
    
    # Method 3: Fallback to direct data store access
    # (implement specific fallbacks for each tool)
    return {"error": "All access methods failed"}
```

---

## 🎯 **CONSOLIDATED PROTOCOLS (User Mentioned)**

**User said:** "we already consolidated mcp tools and are manual organization protocols for cursor IDE"

**I need to find:**
1. Where are the consolidated MCP tools protocols?
2. Where are the manual organization protocols?
3. How do they work together?

**Searching for:**
- `knowledge_architecture/FLOATING_FILES_ORGANIZED/MCP_PROTOCOLS/` - Found MCP protocols
- Manual organization protocols for Cursor IDE
- Hybrid approach documentation

---

## 📋 **IMMEDIATE ACTIONS FOR IDE CONSOLIDATION**

1. ✅ **Use `create_plan`** - Via HTTP or direct Python call
   - Goal: "Consolidate all 6 IDE prototypes + 1 main app = 100+ panels"
   - Context: "Discovery phase - reading panel registries"
   - Priority: Based on OBJ-12 alignment

2. ✅ **Use `add_timeline_entry`** - Track context
   - Every major action
   - Every phase completion
   - Preserve mission awareness

3. ✅ **Use `update_goal_progress`** - Track progress
   - As phases complete
   - Milestone tracking
   - OBJ-12 progress updates

4. ✅ **Use `query_goal_timeline`** - Check alignment
   - Before starting work
   - Validate OBJ-12 alignment
   - Check existing goals

5. ✅ **Use `store_memory`** - Store insights
   - Important findings
   - Panel inventory results
   - Backend API discoveries

---

## 🚨 **CRITICAL: NO MORE EXCUSES**

**I will NOT say:**
- ❌ "MCP tools not available"
- ❌ "Can't use protocols without MCP server"
- ❌ "Waiting for MCP server to start"

**I WILL:**
- ✅ Always try Command Server HTTP first
- ✅ Always fallback to direct Python calls
- ✅ Always fallback to direct data store access
- ✅ ALWAYS follow protocols regardless of MCP server status

---

**Status:** 🔴 **IMPLEMENTING MCP MANUAL ACCESS**  
**Created:** 2025-11-19  
**Purpose:** Access MCP tool data even when MCP server not running

