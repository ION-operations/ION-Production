# 🚨 EMERGENCY DEBUG GUIDE

## FIXED: The "when" clause was blocking the views!

### **The Problem:**
```json
"when": "workspaceFolderCount > 0"  // ❌ This prevented views from showing!
```

If you don't have a workspace open (just random files), the views won't appear!

### **The Fix:**
Removed the `when` clause entirely - views now ALWAYS show!

---

## 🔧 **How to Test the Fix:**

### **Method 1: Reload Window**
```
1. Press: Ctrl+Shift+P
2. Type: Developer: Reload Window
3. Press Enter
```

### **Method 2: Run Debug Dashboard Command**
```
1. Press: Ctrl+Shift+P
2. Type: AIM-OS: Debug Dashboard
3. Press Enter
4. Check Output panel for "AIM-OS Debug" channel
```

### **Method 3: Check Manually**
1. Click the ✨ sparkle icon (left activity bar)
2. Should show dashboard in right sidebar
3. Click bottom panel tab "AIM-OS DevTools"
4. Should show Test Panel

---

## 📊 **What Should Happen:**

### **RIGHT SIDEBAR (Sparkle Icon ✨)**
- Shows "Dashboard" view
- Should display React UI with 6 tabs
- Agents, Chat, Chains, Tools, Timeline, NL Tags

### **BOTTOM PANEL (AIM-OS DevTools Tab)**
- Shows "Test Panel" view
- Green background with "WEBVIEW IS WORKING!"
- Test button to verify JavaScript

---

## 🔍 **If Still Not Working:**

### **Check 1: Extension Activated?**
```
Ctrl+Shift+P → AIM-OS: Show Logs
```
Should show activation logs

### **Check 2: Files Present?**
The VSIX should contain:
- `dist/index.html` (1 KB)
- `dist/assets/` (5 files)
- `out/extension.js` (compiled)

### **Check 3: Console Errors?**
```
Help → Toggle Developer Tools
Check Console tab for errors
```

---

## 🚀 **Emergency Commands:**

### **Force Reinstall:**
```powershell
cd cursor-addon
npm run build
vsce package --out aimos-cursor-addon.vsix
code --install-extension aimos-cursor-addon.vsix --force
```

### **Complete Reset:**
```powershell
# Uninstall first
code --uninstall-extension aimos.aimos-cursor-addon

# Clean build
cd cursor-addon
Remove-Item -Recurse -Force node_modules, out, dist
npm install
npm run build
vsce package --out aimos-cursor-addon.vsix
code --install-extension aimos-cursor-addon.vsix --force
```

---

## 📝 **Latest Fixes Applied:**

1. ✅ **Packaging Fix** - `.vscodeignore` now includes dist/
2. ✅ **Activation Fix** - Changed to `"*"` for universal activation
3. ✅ **When Clause Fix** - Removed workspace requirement
4. ✅ **Logging Added** - AIMOSLogger for debugging
5. ✅ **Architecture Fix** - Dashboard in right, DevTools in bottom

---

## 💡 **Understanding the Architecture:**

```
VS Code UI Structure:
├── ACTIVITY BAR (left icons)
│   ├── Explorer
│   ├── Search
│   ├── Git
│   └── ✨ AIM-OS (our icon)
│
├── SIDEBAR (right panel when icon clicked)
│   └── Dashboard (our React UI)
│
└── PANEL (bottom area)
    ├── Terminal
    ├── Output
    ├── Problems
    └── AIM-OS DevTools (our test panel)
```

---

## 🆘 **Still Broken?**

If none of this works, the nuclear option:

1. **Close Cursor completely**
2. **Delete:** `C:\Users\bombe\.vscode\extensions\aimos.aimos-cursor-addon-*`
3. **Reinstall from scratch**
4. **Open fresh Cursor window**

The issue is DEFINITELY one of:
- Extension not activating
- Files not in VSIX
- Provider not registering
- View IDs mismatched
- When clause blocking

We've now fixed ALL of these! 🎉
