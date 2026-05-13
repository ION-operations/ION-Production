# Complete Restart Guide - AIOS Extension + Electron + MCP Server

**Date:** 2025-01-27  
**Status:** Ready for use

---

## ✅ **STEP 1: Reload Cursor Extension**

**Option A: Command Palette (Recommended)**
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type: `Developer: Reload Window`
3. Press Enter
4. Wait ~2-3 seconds for reload

**Option B: Keyboard Shortcut**
- Press `Ctrl+R` (Windows/Linux) or `Cmd+R` (Mac)

**Option C: Restart Extension Host**
1. Press `Ctrl+Shift+P`
2. Type: `Developer: Restart Extension Host`
3. Press Enter

---

## ✅ **STEP 2: Restart MCP Server** (After Cursor Reloads)

**Via HTTP Endpoint:**
```powershell
Invoke-WebRequest -Uri "http://localhost:5001/mcp/restart" -Method GET
```

**Or via curl:**
```bash
curl http://localhost:5001/mcp/restart
```

**Expected Response:**
```json
{
  "success": true,
  "message": "MCP server restarted successfully"
}
```

---

## ✅ **STEP 3: Verify Everything Works**

**Check Command Server:**
```powershell
Invoke-WebRequest -Uri "http://localhost:5001/health" -Method GET
```

**Test MCP Tools:**
```powershell
$body = @{
  tool = "get_ai_messages"
  arguments = @{ limit = 5 }
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5001/mcp/execute" -Method POST -ContentType "application/json" -Body $body
```

**Check Electron App:**
- Should show top bar, side drawers, bottom bar
- Chat should work
- System tools should be accessible

---

## 🔍 **TROUBLESHOOTING**

### **If Extension Doesn't Reload:**
1. Full restart: Close and reopen Cursor completely
2. Rebuild extension: `cd cursor-addon && npm run compile`
3. Reinstall extension: `cd cursor-addon && npm run package && cursor --install-extension aimos-cursor-addon.vsix --force`

### **If MCP Server Won't Restart:**
1. Check if Command Server is running: `Invoke-WebRequest -Uri "http://localhost:5001/health"`
2. If not running, reload Cursor extension first
3. Check Output panel → "MCP" for connection errors

### **If Electron App Won't Start:**
1. Kill all Electron processes: `Get-Process electron | Stop-Process -Force`
2. Rebuild: `cd packages/ide_chat_app && npm run build`
3. Launch: `npm run electron`

---

## 📋 **COMPLETE RESTART CHECKLIST**

- [ ] Reload Cursor Extension (`Ctrl+Shift+P` → "Developer: Reload Window")
- [ ] Wait for reload to complete (~2-3 seconds)
- [ ] Restart MCP Server (`GET http://localhost:5001/mcp/restart`)
- [ ] Verify Command Server health (`GET http://localhost:5001/health`)
- [ ] Test MCP tools (send message, get messages)
- [ ] Verify Electron app UI (top bar, drawers, bottom bar)
- [ ] Test Electron chat functionality

---

**Status:** ✅ Ready to use  
**Last Updated:** 2025-01-27

