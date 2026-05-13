# ✅ Extension Installation Checklist

**Date:** 2025-01-27  
**Purpose:** Ensure extension installs correctly after 15 failed attempts

---

## 🔍 **PRE-INSTALLATION CHECKS**

### **1. Verify Build Files Exist:**
```powershell
# Check these files exist:
cursor-addon/dist/index.html          # React UI HTML
cursor-addon/dist/assets/*.js         # React UI JavaScript
cursor-addon/dist/assets/*.css        # React UI CSS
cursor-addon/out/extension.js         # Extension JavaScript
cursor-addon/aimos-cursor-addon.vsix  # Packaged extension
```

### **2. Verify Extension Version:**
- Current version: **1.2.0** (updated with extension bridge)
- Check `package.json` shows correct version

### **3. Clear Old Extension:**
```powershell
# Uninstall old version
cursor --uninstall-extension aimos.lucid-ui-aimos

# Or manually remove:
# C:\Users\<username>\.cursor\extensions\aimos.lucid-ui-aimos-*
```

---

## 📦 **INSTALLATION STEPS**

### **Step 1: Package Extension**
```powershell
cd cursor-addon
npm run package
```

**Expected Output:**
- ✅ React UI built
- ✅ Extension compiled
- ✅ `aimos-cursor-addon.vsix` created (should be ~639KB)

### **Step 2: Install Extension**
```powershell
# Find Cursor executable
$cursorPath = "$env:LOCALAPPDATA\Programs\cursor\Cursor.exe"

# Install extension
& $cursorPath --install-extension aimos-cursor-addon.vsix --force
```

**Or use install script:**
```powershell
npm run install:windows
```

### **Step 3: Verify Installation**
1. Open Cursor
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Lucid UI - AIM-OS"
4. Should show version **1.2.0**
5. Should show as **Enabled**

---

## 🔧 **POST-INSTALLATION VERIFICATION**

### **1. Check Extension Loads:**
- Open Developer Tools (Help → Toggle Developer Tools)
- Check Console for: `AIM-OS Cursor Add-on is now active!`
- Should see no errors related to extension

### **2. Check React UI Panel:**
- Click Activity Bar icon (sparkle icon)
- Should see React UI panel in sidebar
- Should show tabs: Agents, Chat, Chains, Tools, Timeline, NL Tags
- Should NOT show old dropdown menus

### **3. Check Extension Bridge:**
- Open Chat tab
- Try sending a message to an agent
- Check Developer Console for MCP tool calls
- Should see `mcpCall` messages being sent

---

## 🐛 **TROUBLESHOOTING**

### **Issue: Extension Not Installing**
**Check:**
- Cursor executable path is correct
- VSIX file exists and is valid
- No conflicting extension versions

**Fix:**
```powershell
# Force uninstall all versions
cursor --uninstall-extension aimos.lucid-ui-aimos --force

# Clean install
cursor --install-extension aimos-cursor-addon.vsix --force
```

### **Issue: Old UI Still Showing**
**Check:**
- Extension version is 1.2.0 (not 1.0.0 or 1.1.0)
- React UI dist files exist in extension
- Webview is loading correct HTML

**Fix:**
- Reload Cursor window (Ctrl+R)
- Reload extension (Developer Tools → Reload Extension)
- Rebuild and reinstall extension

### **Issue: Extension Bridge Not Working**
**Check:**
- MCP server is configured in `~/.cursor/mcp.json`
- MCP tools are available (check tool list)
- Extension console shows no errors

**Fix:**
- Verify MCP server is running
- Check `mcp.json` configuration
- Check extension console for errors

---

## 📋 **DEBUGGING CHECKLIST**

- [ ] Extension version is 1.2.0
- [ ] VSIX file is recent (check timestamp)
- [ ] Old extension uninstalled
- [ ] Cursor restarted after installation
- [ ] React UI panel shows (not old dropdowns)
- [ ] Chat tab works
- [ ] Extension bridge sends MCP calls
- [ ] No errors in Developer Console

---

## 💙 **HOPING THIS WORKS!**

After 15 restarts, we really hope this time works! The extension bridge is implemented and packaged. Everything should be ready! 🤞

---

**If it still doesn't work, let's debug together!** We'll figure it out! 💙

