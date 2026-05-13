# MCP Pythonpath Critical Lesson

**Date:** 2025-10-25  
**Severity:** CRITICAL  
**Impact:** MCP server won't start without this

---

## 🎯 THE LESSON

**Problem:** MCP server not starting in Cursor  
**Root Cause:** Missing `env.PYTHONPATH` in `c:\Users\bombe\.cursor\mcp.json`

---

## 💡 WHY IT MATTERS

AIM-OS MCP servers need to import packages:
```python
from cmc_service import MemoryStore
from cmc_service.models import AtomCreate
```

**Without PYTHONPATH:**
- Python searches standard paths
- Can't find `packages/cmc_service/`
- Import fails → Server crashes
- Tools unavailable

**With PYTHONPATH:**
- Python searches `C:\Users\bombe\OneDrive\Desktop\AIM-OS`
- Finds `packages/` directory
- Imports succeed
- Server starts successfully

---

## ✅ CORRECT CONFIGURATION

Always include this in `mcp.json`:

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

---

## 🚨 REMEMBER

**For ANY MCP server importing AIM-OS packages, you MUST include:**
```json
"env": {
  "PYTHONPATH": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
}
```

**This is not optional. This is required.**

---

## 📚 RELATED LESSONS

- `-u` flag required for unbuffered I/O (stdio transport)
- Use absolute paths with `\\` backslashes on Windows
- Always set `cwd` to project root
- **Always include `env.PYTHONPATH`**

**Status:** LEARNED - Will never forget this requirement 💡
