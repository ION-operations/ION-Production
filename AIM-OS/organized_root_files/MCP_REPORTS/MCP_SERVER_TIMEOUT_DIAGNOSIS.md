# MCP Server Timeout Diagnosis & Fix
**Date:** 2025-11-01  
**Issue:** `get_ai_messages` timing out - MCP server not responding

---

## 🔴 **CRITICAL FINDING**

**Error from Extension Logs:**
```
Request timeout after 30s for tool: get_ai_messages
```

**Root Cause:** MCP server process is NOT responding to requests. The 30-second timeout indicates the server isn't communicating properly.

---

## 🔍 **POTENTIAL CAUSES**

### **1. MCP Server Not Starting**
- Python process may crash on startup
- Import errors (CMC, HHNI, VIF dependencies)
- Missing PYTHONPATH environment variable
- Server crashes before responding to `initialize`

### **2. Server Hanging During Initialization**
- CMC service initialization blocking
- HHNI index loading blocking
- Server waiting for something that never comes

### **3. Communication Issue**
- Server not flushing stdout properly
- Extension not reading stdout correctly
- Buffer issues with stdio transport

### **4. Wrong Server File**
- Extension was looking for `run_mcp_cross_model.py` (doesn't exist)
- **FIXED:** Now defaults to `lucid_mcp_server.py` ✅

---

## ✅ **FIXES APPLIED**

### **1. Fixed MCP Server Path**
- **Before:** `run_mcp_cross_model.py` (non-existent)
- **After:** `lucid_mcp_server.py` (exists, has all 59 tools)

### **2. Increased Timeout**
- **Before:** 30 seconds
- **After:** 60 seconds
- Allows more time for complex operations

### **3. Added Startup Delay**
- Added 1-second delay before sending `initialize` request
- Gives server time to fully start

### **4. Enhanced Error Logging**
- Logs MCP server stderr output
- Logs process exit codes
- Logs initialization errors with context
- Better timeout error messages (includes tool name)

---

## 🚨 **NEXT STEPS TO DIAGNOSE**

### **Step 1: Check if Server Starts**
```bash
python -u lucid_mcp_server.py
```
- Should start and wait for JSON-RPC input
- Should NOT crash immediately
- Look for error messages in stderr

### **Step 2: Test Initialize Request**
Send this to the running server:
```json
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}
```
- Should respond with initialize result
- If no response, server is hanging

### **Step 3: Check Extension Logs**
- View → Output → Select "AIM-OS Extension"
- Look for:
  - `[MCPClient] MCP Server stderr:` messages
  - `[MCPClient] MCP Server process exited` messages
  - `[MCPClient] MCP Server process error` messages

### **Step 4: Check Python Dependencies**
```bash
python -c "import sys; sys.path.insert(0, 'packages'); from cmc_service import MemoryStore; print('OK')"
```
- Should succeed without errors
- If fails, missing dependencies

---

## 🛠️ **IF SERVER STILL NOT RESPONDING**

### **Option 1: Use Working MCP Server**
Switch to `run_mcp_6_tools.py` (known working):
```json
"aimos.mcpServerPath": "run_mcp_6_tools.py"
```

### **Option 2: Check PYTHONPATH**
Ensure Python can find packages:
```bash
$env:PYTHONPATH = "C:\Users\bombe\OneDrive\Desktop\AIM-OS"
```

### **Option 3: Test Server Manually**
Run server in terminal, send test requests, verify it responds.

---

## 📊 **EXPECTED BEHAVIOR**

1. Extension spawns Python process: `python -u lucid_mcp_server.py`
2. Server starts, logs to stderr: `[AIM-OS-MCP] Initializing...`
3. Extension sends `initialize` request via stdin
4. Server responds via stdout: `{"jsonrpc": "2.0", "id": 1, "result": {...}}`
5. Extension receives response, MCP client initialized
6. Tool calls work normally

**Current Failure:** Step 4 - Server not responding

---

**Status:** Diagnosis complete, fixes applied  
**Action Required:** Test if server starts manually, check extension logs  
**Priority:** CRITICAL - Chat interface completely broken

