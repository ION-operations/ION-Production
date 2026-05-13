# Electron Console Capture - Testing Guide

**Date:** 2025-01-27  
**Status:** ✅ **READY FOR TESTING**

---

## ✅ **IMPLEMENTATION COMPLETE**

All code changes have been implemented:
- ✅ Electron main.js enhanced with logging
- ✅ Electron preload.js enhanced with console capture
- ✅ Command Server endpoint added
- ✅ MCP tool added
- ✅ Extension compiled and installed

---

## 🧪 **TESTING STEPS**

### **Step 1: Restart Electron App**
The Electron app needs to be restarted to enable the new logging functionality.

```batch
cd packages/ide_chat_app
.\LAUNCH_ELECTRON.bat
```

**Or manually:**
```bash
cd packages/ide_chat_app
npm run electron
```

### **Step 2: Generate Some Logs**
In the Electron app, do something that generates console output:
- Open DevTools (should auto-open in dev mode)
- Check console for messages
- The app should log startup messages automatically

### **Step 3: Test MCP Tool**
Use the `get_electron_logs` MCP tool:

```python
# Get all recent logs
get_electron_logs(limit=100)

# Get only errors
get_electron_logs(limit=50, level="error")

# Get main process logs
get_electron_logs(limit=100, source="main")

# Get renderer console logs
get_electron_logs(limit=50, source="renderer")
```

### **Step 4: Verify Log File**
Check if log file exists:

**Windows:**
```powershell
Test-Path "$env:APPDATA\AIM-OS Dashboard\electron-console.log"
Get-Content "$env:APPDATA\AIM-OS Dashboard\electron-console.log" -Tail 20
```

### **Step 5: Test HTTP Endpoint**
Test the Command Server endpoint directly:

```powershell
$response = Invoke-WebRequest -Uri "http://localhost:5001/cursor/electron/logs?limit=50" -Method GET -ErrorAction SilentlyContinue
if ($response) { $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10 }
```

---

## 📊 **EXPECTED RESULTS**

### **Successful Test:**
```json
{
    "success": true,
    "logs": [
        "[2025-01-27T21:10:00.123Z] [LOG] [MAIN] 🚀 Electron app starting...",
        "[2025-01-27T21:10:00.456Z] [LOG] [MAIN] Log file: C:\\Users\\...\\electron-console.log",
        "[2025-01-27T21:10:03.789Z] [LOG] [RENDERER] ✅ AIM-OS Electron preload script loaded"
    ],
    "count": 3,
    "total_lines": 3,
    "log_file": "C:\\Users\\...\\electron-console.log",
    "level_filter": "all",
    "source_filter": "all"
}
```

### **If Log File Not Found:**
```json
{
    "success": false,
    "error": "Electron log file not found at: ... Is Electron app running?",
    "log_file": "..."
}
```

---

## 🔍 **TROUBLESHOOTING**

### **Issue: Log file not found**
**Cause:** Electron app not running or not restarted  
**Solution:** 
1. Restart Electron app
2. Check log file path matches Electron's `app.getPath('userData')`

### **Issue: No logs captured**
**Cause:** Console override not working  
**Solution:**
1. Check Electron DevTools console for errors
2. Verify preload script loaded correctly
3. Check IPC handler registered

### **Issue: MCP tool fails**
**Cause:** Command Server not running or extension not loaded  
**Solution:**
1. Reload Cursor window
2. Check Command Server health: `GET http://localhost:5001/health`
3. Verify extension activated

---

## ✅ **SUCCESS CRITERIA**

- ✅ Electron app starts without errors
- ✅ Log file created at expected location
- ✅ Logs captured from main process
- ✅ Logs captured from renderer process
- ✅ MCP tool returns logs successfully
- ✅ HTTP endpoint returns logs successfully
- ✅ Filtering by level works
- ✅ Filtering by source works

---

**Status:** ✅ **Ready for Testing**  
**Next:** Restart Electron app and test MCP tool

---

*Testing Guide by Aether*  
*2025-01-27*

