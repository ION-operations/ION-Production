# Electron Console Capture MCP Tool - Research & Implementation Plan

**Date:** 2025-01-27  
**Status:** ✅ **IMPLEMENTATION PLAN**

---

## 🎯 **GOAL**

Create MCP tools to capture and view console messages from Electron apps in Cursor, enabling real-time debugging of Electron applications.

**Benefits:**
- 🔍 **Real-time debugging** - See Electron console output instantly
- 📊 **Main process logs** - Capture main process stdout/stderr
- 🌐 **Renderer process logs** - Capture renderer console messages
- 🚀 **Better debugging** - No need to manually check Electron DevTools

---

## 📚 **ELECTRON CONSOLE CAPTURE METHODS**

### **Method 1: File-Based Logging** ✅ **RECOMMENDED**
**Approach:** Electron writes logs to file, MCP tool reads file
- ✅ Simple to implement
- ✅ Persistent logs
- ✅ Works even if Electron crashes
- ✅ No IPC overhead

### **Method 2: IPC-Based Logging**
**Approach:** Electron sends logs via IPC to extension
- ✅ Real-time capture
- ⚠️ Requires IPC setup
- ⚠️ More complex

### **Method 3: HTTP Endpoint**
**Approach:** Electron exposes HTTP endpoint for logs
- ✅ Real-time capture
- ⚠️ Requires HTTP server in Electron
- ⚠️ Additional complexity

### **Method 4: DevTools Protocol**
**Approach:** Use Electron's DevTools Protocol to capture console
- ✅ Can capture renderer console
- ⚠️ Complex setup
- ⚠️ Requires DevTools connection

---

## 🛠️ **IMPLEMENTATION PLAN**

### **Phase 1: Enhanced Electron Logging**

**File:** `packages/ide_chat_app/electron/main.js`

**Add:**
1. **Log File Writer** - Write all console.log/error/warn to file
2. **Renderer Console Capture** - Capture renderer console via IPC
3. **Log Rotation** - Prevent log files from growing too large
4. **Log Format** - Timestamp, level, source (main/renderer), message

```javascript
// Enhanced logging system
const logFile = path.join(app.getPath('userData'), 'electron-logs.txt');
const maxLogSize = 10 * 1024 * 1024; // 10MB

function writeLog(level, source, message) {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] [${level}] [${source}] ${message}\n`;
    
    // Write to file
    fs.appendFileSync(logFile, logEntry);
    
    // Also output to console
    console[level](`[${source}] ${message}`);
    
    // Rotate if too large
    if (fs.existsSync(logFile)) {
        const stats = fs.statSync(logFile);
        if (stats.size > maxLogSize) {
            // Keep last 5MB
            const content = fs.readFileSync(logFile, 'utf8');
            const lines = content.split('\n');
            const keepLines = lines.slice(-50000); // Keep last 50k lines
            fs.writeFileSync(logFile, keepLines.join('\n'));
        }
    }
}

// Override console methods
const originalLog = console.log;
console.log = (...args) => {
    writeLog('log', 'MAIN', args.join(' '));
    originalLog(...args);
};

const originalError = console.error;
console.error = (...args) => {
    writeLog('error', 'MAIN', args.join(' '));
    originalError(...args);
};

const originalWarn = console.warn;
console.warn = (...args) => {
    writeLog('warn', 'MAIN', args.join(' '));
    originalWarn(...args);
};
```

**Capture Renderer Console:**
```javascript
// Capture renderer console messages
mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
    writeLog(level === 0 ? 'log' : level === 1 ? 'warn' : 'error', 'RENDERER', message);
});

// Also capture via IPC
ipcMain.handle('electron-console-log', (event, { level, message }) => {
    writeLog(level, 'RENDERER', message);
});
```

### **Phase 2: Command Server Endpoint**

**File:** `cursor-addon/src/commandServer.ts`

**Add:**
```typescript
// GET /cursor/electron/logs
if (pathname === '/cursor/electron/logs') {
    const limit = query.limit ? parseInt(query.limit as string, 10) : 100;
    const level = query.level as string; // 'log', 'error', 'warn', 'all'
    const source = query.source as string; // 'main', 'renderer', 'all'
    const result = await this.handleGetElectronLogs(limit, level, source);
    this.sendSuccess(res, result);
    return;
}
```

**Handler:**
```typescript
private async handleGetElectronLogs(
    limit: number,
    level?: string,
    source?: string
): Promise<any> {
    try {
        // Get Electron log file path
        const electronLogPath = path.join(
            process.env.APPDATA || process.env.HOME || '',
            'AIM-OS Dashboard',
            'electron-logs.txt'
        );
        
        if (!fs.existsSync(electronLogPath)) {
            return {
                success: false,
                error: 'Electron log file not found. Is Electron app running?'
            };
        }
        
        // Read and filter logs
        const content = fs.readFileSync(electronLogPath, 'utf8');
        let lines = content.split('\n').filter(l => l.trim());
        
        // Filter by level
        if (level && level !== 'all') {
            lines = lines.filter(l => l.includes(`[${level}]`));
        }
        
        // Filter by source
        if (source && source !== 'all') {
            lines = lines.filter(l => l.includes(`[${source}]`));
        }
        
        // Get last N lines
        const logs = lines.slice(-limit);
        
        return {
            success: true,
            logs,
            count: logs.length,
            total_lines: lines.length,
            log_file: electronLogPath
        };
    } catch (error: any) {
        return {
            success: false,
            error: error.message || String(error)
        };
    }
}
```

### **Phase 3: MCP Tool**

**File:** `lucid_mcp_server.py`

**Add Tool:**
```python
# Tool 69: get_electron_logs
{
    "name": "get_electron_logs",
    "description": "Get console logs from Electron application. Captures main process and renderer process console messages.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Maximum number of log lines to return",
                "default": 100
            },
            "level": {
                "type": "string",
                "description": "Filter by log level: 'log', 'error', 'warn', 'all'",
                "enum": ["log", "error", "warn", "all"],
                "default": "all"
            },
            "source": {
                "type": "string",
                "description": "Filter by source: 'main', 'renderer', 'all'",
                "enum": ["main", "renderer", "all"],
                "default": "all"
            }
        },
        "required": []
    }
}
```

**Handler:**
```python
def get_electron_logs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get console logs from Electron application"""
    try:
        limit = arguments.get("limit", 100)
        level = arguments.get("level", "all")
        source = arguments.get("source", "all")
        
        endpoint = f"/cursor/electron/logs?limit={limit}"
        if level != "all":
            endpoint += f"&level={level}"
        if source != "all":
            endpoint += f"&source={source}"
        
        result = self._call_command_server(endpoint, "GET")
        if not result.get("success"):
            return result
        
        logs = result.get("logs", [])
        return {
            "success": True,
            "logs": logs,
            "count": len(logs),
            "total_lines": result.get("total_lines", 0),
            "log_file": result.get("log_file", ""),
            "level_filter": level,
            "source_filter": source,
            "message": f"Retrieved {len(logs)} log lines from Electron app"
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to get Electron logs: {str(e)}"}
```

---

## 📊 **PROPOSED MCP TOOLS**

### **1. get_electron_logs**
**Purpose:** Get console logs from Electron application  
**Parameters:**
- `limit` (integer, optional): Max lines to return (default: 100)
- `level` (string, optional): Filter by level: 'log', 'error', 'warn', 'all' (default: 'all')
- `source` (string, optional): Filter by source: 'main', 'renderer', 'all' (default: 'all')

**Returns:**
- Log lines array
- Total line count
- Log file path
- Filter information

### **2. get_electron_log_summary** (Future)
**Purpose:** Get summary statistics of Electron logs  
**Parameters:**
- None

**Returns:**
- Error count
- Warning count
- Log count
- Last log timestamp

### **3. tail_electron_logs** (Future)
**Purpose:** Get real-time log updates (tail functionality)  
**Parameters:**
- `since` (timestamp, optional): Get logs since timestamp

**Returns:**
- New log lines since last check

---

## ✅ **IMPLEMENTATION CHECKLIST**

- [ ] Enhance Electron main.js with file-based logging
- [ ] Capture renderer console messages via IPC
- [ ] Add Command Server endpoint `/cursor/electron/logs`
- [ ] Add MCP tool `get_electron_logs`
- [ ] Test log capture from Electron app
- [ ] Document usage

---

## 🎯 **USE CASES**

### **1. Real-Time Debugging:**
```python
# Check Electron errors
get_electron_logs(limit=50, level="error")

# Check main process logs
get_electron_logs(limit=100, source="main")

# Check renderer console
get_electron_logs(limit=50, source="renderer")
```

### **2. Debugging Electron App:**
```python
# See all recent logs
get_electron_logs(limit=200)

# Check for errors
get_electron_logs(level="error")

# Check main process only
get_electron_logs(source="main", limit=50)
```

---

## 📊 **EXPECTED BENEFITS**

**Before:**
- ❌ Need to manually open Electron DevTools
- ❌ Can't see main process logs easily
- ❌ No centralized log access

**After:**
- ✅ See Electron logs instantly in Cursor
- ✅ Filter by level and source
- ✅ Centralized log access via MCP
- ✅ Real-time debugging capability

---

**Status:** ✅ **Ready to implement**  
**Priority:** HIGH (Major debugging capability improvement)  
**Confidence:** 0.85 (Electron API supports this)

---

*Research & Implementation Plan by Aether*  
*2025-01-27*

