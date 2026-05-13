# 🔄 MCP Server Restart - Quick Fix Guide

**Date:** 2025-01-27  
**Status:** ✅ **READY TO APPLY**

---

## 🎯 **THE PROBLEM**

Chat only shows:
- ✅ 1 message from Aether
- ❌ 0 messages from Sev (but they exist!)
- ✅ Some messages from electron-app

**Root Cause:** MCP server process is using old code (before Sev's merge fix)

---

## ✅ **THE FIX**

**Reload Cursor Window** to restart the MCP server process

### **Quick Steps:**

1. **Press `Ctrl+Shift+P`** (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. **Type:** `Reload Window`
3. **Select:** `Developer: Reload Window`
4. **Wait** for Cursor to reload (~5 seconds)
5. **Test chat** - should now show all messages!

---

## 🔍 **VERIFICATION**

After reload, test Command Server:

```powershell
$body = @{tool="get_ai_messages";arguments=@{limit=30}} | ConvertTo-Json
$response = Invoke-WebRequest -Uri "http://localhost:5001/mcp/execute" -Method POST -ContentType "application/json" -Body $body
$result = $response.Content | ConvertFrom-Json
Write-Host "✅ Message count: $($result.result.count)"
$result.result.messages | Group-Object from_ai | Format-Table Name,Count
```

**Expected Result:**
```
✅ Message count: 13+
Name       Count
----       -----
Aether     3+
Sev        6+
Max        1+
electron-app 3+
```

---

## 📊 **WHAT HAPPENS**

When you reload Cursor:

1. ✅ Extension reloads
2. ✅ `MCPClient` reinitializes
3. ✅ New Python process spawns: `python -u lucid_mcp_server.py`
4. ✅ Loads updated code with Sev's merge fix
5. ✅ Command Server returns all messages (CMC + in-memory)

---

## 🎯 **WHY THIS WORKS**

**Sev's Fix:**
- Merges CMC messages + in-memory messages (lines 5692-5713)
- Code is correct ✅
- Process just needs restart to load new code

**Current State:**
- Old process: Only returns CMC messages (6 total)
- New process: Returns merged messages (13+ total)

---

## ✅ **AFTER RELOAD**

Chat should show:
- ✅ All Aether messages
- ✅ All Sev messages
- ✅ All Max messages
- ✅ All electron-app messages

**Status:** Ready to reload! 🚀

---

*Quick fix guide by Aether*  
*2025-01-27*

