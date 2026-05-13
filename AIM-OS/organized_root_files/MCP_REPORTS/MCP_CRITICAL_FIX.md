# MCP Server Critical Fix - PYTHONPATH Missing
**Date:** 2025-11-01  
**Issue:** MCP server crashing on startup - ModuleNotFoundError: No module named 'cmc_service'

---

## 🔴 **ROOT CAUSE IDENTIFIED**

**Problem:** Extension spawns Python MCP server **without PYTHONPATH environment variable**

**Result:** 
- Python can't find `packages/cmc_service/`
- Server crashes on import
- Never responds to `initialize` request
- Extension times out after 30 seconds

**Evidence:**
```bash
python -c "import sys; sys.path.insert(0, 'packages'); from cmc_service import MemoryStore"
# Result: ModuleNotFoundError: No module named 'cmc_service'
```

---

## ✅ **FIX APPLIED**

### **Added PYTHONPATH to Extension Spawn**

**File:** `cursor-addon/src/mcp/mcpClient.ts`

**Before:**
```typescript
this.process = spawn('python', ['-u', mcpServerPath], {
    cwd: workspaceRoot,
    stdio: ['pipe', 'pipe', 'pipe']
});
```

**After:**
```typescript
this.process = spawn('python', ['-u', mcpServerPath], {
    cwd: workspaceRoot,
    stdio: ['pipe', 'pipe', 'pipe'],
    env: {
        ...process.env,
        PYTHONPATH: workspaceRoot, // CRITICAL: Allows Python to find packages/
        PYTHONUNBUFFERED: '1' // Ensure unbuffered output
    }
});
```

---

## 🎯 **WHY THIS FIXES IT**

1. **PYTHONPATH set:** Python now searches workspace root for modules
2. **Finds packages/:** Python can import `cmc_service`, `hhni`, `vif`, etc.
3. **Server starts:** MCP server initializes successfully
4. **Responds to requests:** Server can handle `initialize` and `tools/call`

---

## 📋 **TESTING CHECKLIST**

After extension recompiles and reloads:

1. ✅ Check Extension Logs:
   - View → Output → "AIM-OS Extension"
   - Should see: `[MCPClient] Starting MCP server: lucid_mcp_server.py`
   - Should see: `[MCPClient] PYTHONPATH: C:\Users\bombe\...`
   - Should NOT see: `ModuleNotFoundError` or crash messages

2. ✅ Test MCP Tool:
   - Electron app → Chat tab
   - Should be able to retrieve messages
   - Should NOT timeout

3. ✅ Verify Server Starts:
   - Extension logs should show successful initialization
   - No stderr errors about missing modules

---

## 🚨 **IF STILL FAILING**

### **Check 1: Verify File Exists**
```bash
Test-Path "lucid_mcp_server.py"
Test-Path "packages\cmc_service"
```

### **Check 2: Test Import Manually**
```bash
$env:PYTHONPATH = "C:\Users\bombe\OneDrive\Desktop\AIM-OS"
python -c "import sys; sys.path.insert(0, 'packages'); from cmc_service import MemoryStore; print('OK')"
```

### **Check 3: Check Extension Logs**
- Look for stderr output from MCP server
- Check for Python import errors
- Verify PYTHONPATH is set correctly

---

**Status:** Fix applied - PYTHONPATH now set when spawning server  
**Impact:** Should fix timeout issues - server can now import dependencies  
**Next:** Recompile extension, reload Cursor, test chat interface

