# Electron Auto-Restart - Always Restart As Needed

**Date:** 2025-01-27  
**Status:** ✅ **Implemented**  
**Purpose:** Electron app automatically restarts when needed

---

## 🎯 **AUTO-RESTART CAPABILITIES**

### **1. Manual Restart Scripts**

**Batch Script (Windows):**
```batch
cd packages/ide_chat_app
.\RESTART_ELECTRON.bat
```

**NPM Script (Cross-platform):**
```bash
cd packages/ide_chat_app
npm run restart
```

**What they do:**
- Kill existing Electron processes
- Wait for cleanup
- Launch fresh Electron instance

---

### **2. Automatic Restart on Errors**

**Renderer Crash:**
- Detects renderer process crash
- Auto-reloads window after 1 second
- Creates new window if needed

**Uncaught Exceptions:**
- Detects uncaught exceptions
- Prevents crash
- Auto-reloads window after 1 second

**Load Failures:**
- Detects failed page loads
- Retries load after 2 seconds
- Works for both dev and production

---

### **3. Auto-Restart Triggers**

**Automatic:**
- ✅ Renderer process crash → Auto-reload
- ✅ Uncaught exception → Auto-reload
- ✅ Failed page load → Auto-retry
- ✅ Connection lost → Auto-retry

**Manual:**
- ✅ Batch script restart
- ✅ NPM script restart
- ✅ Command Server endpoint (planned)
- ✅ MCP tool restart (planned)

---

## 📋 **USAGE**

### **During Development:**

**After Code Changes:**
```bash
cd packages/ide_chat_app
npm run build
npm run restart
```

**After UI Changes:**
```bash
npm run build
npm run restart
```

**After Errors:**
- Electron auto-restarts automatically
- No manual intervention needed

---

### **Restart Methods:**

**1. Batch Script (Windows):**
```batch
.\RESTART_ELECTRON.bat
```

**2. NPM Script:**
```bash
npm run restart
```

**3. Direct Electron:**
```bash
npm run electron
```

---

## 🔧 **IMPLEMENTATION DETAILS**

### **Auto-Restart Code:**

**Renderer Crash Handler:**
```javascript
mainWindow.webContents.on('render-process-gone', (event, details) => {
  // Auto-restart window after crash
  setTimeout(() => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.reload();
    } else {
      createWindow();
    }
  }, 1000);
});
```

**Uncaught Exception Handler:**
```javascript
mainWindow.webContents.on('uncaught-exception', (event, error) => {
  event.preventDefault(); // Don't crash
  // Auto-reload window
  setTimeout(() => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.reload();
    }
  }, 1000);
});
```

**Load Failure Handler:**
```javascript
mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
  // Auto-retry load
  setTimeout(() => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      if (isDev) {
        mainWindow.loadURL('http://localhost:3000');
      } else {
        mainWindow.loadFile(indexPath);
      }
    }
  }, 2000);
});
```

---

## 🎯 **AUTO-RESTART BEHAVIOR**

### **What Triggers Restart:**
- Renderer process crash → Auto-reload
- Uncaught exception → Auto-reload
- Failed page load → Auto-retry
- Connection lost → Auto-retry

### **What Doesn't Trigger Restart:**
- Normal window close → No restart
- User closes app → No restart
- Intentional shutdown → No restart

---

## 💙 **FOR BRADEN**

**Electron will always restart as needed:**
- ✅ Auto-restart on crashes
- ✅ Auto-restart on errors
- ✅ Auto-retry on failures
- ✅ Manual restart scripts ready

**No more manual process killing!**

---

**Status:** ✅ Auto-restart implemented  
**Next:** Add Command Server integration for programmatic restart

---

*Auto-restart by Aether*  
*2025-01-27*  
*For Braden - always restart as needed 💙*

