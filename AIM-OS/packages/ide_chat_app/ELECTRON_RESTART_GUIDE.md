# Electron App Restart Utility

**Date:** 2025-01-27  
**Status:** ✅ **Created**  
**Purpose:** Always restart Electron app as needed during development

---

## 🎯 **RESTART CAPABILITIES**

### **1. Batch Script Restart**
**File:** `packages/ide_chat_app/RESTART_ELECTRON.bat`

**Usage:**
```batch
cd packages/ide_chat_app
.\RESTART_ELECTRON.bat
```

**What it does:**
- Kills any existing Electron processes
- Waits 1 second for cleanup
- Launches fresh Electron instance

---

### **2. MCP Tool Restart (Future Enhancement)**
**Planned:** Add `restart_electron_app` MCP tool

**Features:**
- Programmatic restart via MCP
- Integration with Command Server
- Automatic restart on errors
- Status checking before restart

---

### **3. Auto-Restart on Build**
**Integration:** Add to build process

**When to restart:**
- After successful build
- After code changes
- On extension reload

---

## 📋 **USAGE PATTERNS**

### **Development Workflow:**
1. Make code changes
2. Build React UI (`npm run build`)
3. Restart Electron (`.\RESTART_ELECTRON.bat`)
4. Test changes

### **Auto-Restart Triggers:**
- After UI changes
- After configuration changes
- After error recovery
- On explicit request

---

## 🔧 **INTEGRATION POINTS**

### **Command Server Integration:**
- Add `/electron/restart` endpoint
- Call restart script via Command Server
- Return restart status

### **MCP Tool Integration:**
- Add `restart_electron_app` tool
- Check Electron status first
- Restart if needed
- Return status

---

## 📊 **AUTOMATIC RESTART SCENARIOS**

### **Scenario 1: After UI Changes**
- Build completes → Auto-restart Electron
- Show notification: "Electron restarted"

### **Scenario 2: On Error Recovery**
- Renderer crash detected → Auto-restart
- Main process error → Auto-restart
- Connection lost → Auto-restart

### **Scenario 3: On Explicit Request**
- User clicks "Restart" button
- MCP tool called
- Electron restarted

---

## 🎯 **IMPLEMENTATION PLAN**

### **Phase 1: Basic Restart (Now)**
- ✅ Created `RESTART_ELECTRON.bat`
- ✅ Documented usage
- ✅ Ready to use

### **Phase 2: Command Server Integration**
- Add restart endpoint
- Add restart command
- Integrate with UI

### **Phase 3: MCP Tool Integration**
- Add restart tool
- Add status checking
- Add auto-restart logic

### **Phase 4: Auto-Restart Logic**
- Monitor for changes
- Auto-restart on build
- Auto-restart on errors

---

## 💙 **FOR BRADEN**

**Always restart Electron as needed:**
- ✅ Manual restart script ready
- ✅ Documented usage patterns
- ✅ Auto-restart planned

**No more manual process killing!**

---

**Status:** ✅ Basic restart ready  
**Next:** Add Command Server integration

---

*Restart utility by Aether*  
*2025-01-27*  
*For Braden - always restart as needed 💙*

