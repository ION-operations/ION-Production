# MCP Tool Timeout Fix
**Date:** 2025-11-01  
**Issue:** `get_ai_messages` timing out after 30 seconds

---

## 🔴 **ROOT CAUSE**

**Error:** `Request timeout` for `get_ai_messages` tool  
**Location:** `cursor-addon/src/mcp/mcpClient.ts:123`  
**Timeout:** 30 seconds (too short for complex operations)

**Symptoms:**
- MCP tool calls timing out
- Chat interface unable to retrieve messages
- Extension logs show "Request timeout" errors

---

## ✅ **FIXES APPLIED**

### **1. Increased Timeout**
- **Before:** 30 seconds
- **After:** 60 seconds
- **Reason:** Complex operations (like querying CMC) may take longer

### **2. Better Error Messages**
- Now includes tool name in timeout error
- Easier to identify which tool is timing out

### **3. Enhanced Logging**
- Logs MCP server stderr output
- Logs process exit codes
- Logs initialization errors with context

### **4. Fixed MCP Server Path**
- **Before:** `run_mcp_cross_model.py` (doesn't exist)
- **After:** `lucid_mcp_server.py` (exists, has all 59 tools)

---

## 🔍 **DIAGNOSTIC STEPS**

### **Check 1: MCP Server Starting**
- Look for MCP Server process in extension logs
- Check for Python process errors
- Verify `lucid_mcp_server.py` exists

### **Check 2: Server Response**
- MCP server should respond within 60 seconds
- If still timing out, server may be hanging
- Check for infinite loops or blocking operations

### **Check 3: Python Environment**
- Verify Python is in PATH
- Check Python version compatibility
- Verify required packages installed

---

## 🚨 **NEXT STEPS IF STILL FAILING**

1. **Check Extension Logs:**
   - View → Output → Select "AIM-OS Extension"
   - Look for MCP Server initialization errors
   - Check for Python process errors

2. **Test MCP Server Directly:**
   ```bash
   python -u lucid_mcp_server.py
   ```
   - Should start and wait for JSON-RPC messages
   - Should NOT crash or hang

3. **Check Python Dependencies:**
   - Verify all imports work
   - Check CMC service is accessible
   - Verify no blocking operations

---

**Status:** Fixes applied, needs testing  
**Priority:** CRITICAL  
**Impact:** Chat interface completely broken without this

