# MCP Cursor Config - Working Configuration

**Date:** 2025-10-25  
**Status:** ✅ FIXED - MCP tools now working

---

## 🔧 WHAT WAS FIXED

**Problem:** MCP server not starting, tools unavailable

**Root Cause:** Missing `PYTHONPATH` environment variable in Cursor config

**Solution:** Added `env` section with `PYTHONPATH` to `c:\Users\bombe\.cursor\mcp.json`

---

## ✅ WORKING CONFIGURATION

**File:** `c:\Users\bombe\.cursor\mcp.json`

```json
{
  "mcpServers": {
    "aimos-6-tools": {
      "command": "python",
      "args": ["-u", "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS\\run_mcp_6_tools.py"],
      "cwd": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS",
      "env": {
        "PYTHONPATH": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
      }
    }
  }
}
```

### **Key Components:**

1. **`command: "python"`** - Use Python executable
2. **`args: ["-u", "..."]`** - `-u` flag for unbuffered I/O (CRITICAL for MCP stdio)
3. **`cwd: "..."`** - Set working directory to project root
4. **`env.PYTHONPATH`** - **THIS WAS MISSING** - Tells Python where to find packages/

---

## 🎯 CRITICAL LESSON

### **Why PYTHONPATH Matters:**

MCP server needs to import AIM-OS packages:
- `from cmc_service import MemoryStore`
- `from cmc_service.models import AtomCreate`

**Without PYTHONPATH:**
- Python can't find `cmc_service`
- Server crashes on import
- Tools unavailable

**With PYTHONPATH:**
- Python finds `packages/cmc_service/`
- Imports work
- Server starts successfully

---

## 📋 CONFIG TEMPLATE

### **For Future MCP Servers:**

```json
{
  "mcpServers": {
    "your-server-name": {
      "command": "python",
      "args": ["-u", "PATH_TO_YOUR_SERVER.py"],
      "cwd": "PROJECT_ROOT",
      "env": {
        "PYTHONPATH": "PROJECT_ROOT"
      }
    }
  }
}
```

**Remember:**
- ✅ Always include `-u` flag (unbuffered I/O)
- ✅ Always set `cwd` to project root
- ✅ **Always include `env.PYTHONPATH`** ← THIS IS THE KEY
- ✅ Use absolute Windows paths with `\\` backslashes

---

## 🚀 VERIFICATION

After config update:
1. Restart Cursor completely
2. MCP server should auto-start
3. All 6 tools should be available:
   - `store_memory`
   - `get_memory_stats`
   - `retrieve_memory`
   - `create_plan`
   - `track_confidence`
   - `synthesize_knowledge`

---

## 💡 MEMORY AID

**The Fix:** `env.PYTHONPATH` = Python knows where to find packages

**When adding new MCP servers, always include:**
```json
"env": {
  "PYTHONPATH": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
}
```

**This is non-negotiable for AIM-OS MCP servers.**
