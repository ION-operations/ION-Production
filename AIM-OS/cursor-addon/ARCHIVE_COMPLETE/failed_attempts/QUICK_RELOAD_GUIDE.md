# Quick Reload Guide - Testing UI Panel Fix

**Date:** 2025-01-27  
**Issue:** Testing asset path fix for React UI loading

---

## ✅ **OPTION 1: Quick Reinstall (Recommended)**

Since we already ran `npm run build`, you just need to:

### **Step 1: Package & Reinstall**
```powershell
cd cursor-addon
npm run package
cursor --install-extension aimos-cursor-addon.vsix --force
```

**OR use the install script (does everything):**
```powershell
cd cursor-addon
npm run install:windows
```

### **Step 2: Reload Cursor**
- Press `Ctrl+Shift+P`
- Type: `Developer: Reload Window`
- Press Enter

**That's it!** The `--force` flag automatically overwrites the old extension.

---

## 🔄 **OPTION 2: Manual Uninstall First**

If you prefer to uninstall first:

### **Step 1: Uninstall Extension**
1. Open Cursor
2. Go to Extensions (Ctrl+Shift+X)
3. Find "Lucid UI - AIM-OS"
4. Click the gear icon → Uninstall

### **Step 2: Rebuild & Install**
```powershell
cd cursor-addon
npm run build
npm run package
cursor --install-extension aimos-cursor-addon.vsix
```

### **Step 3: Reload**
- Press `Ctrl+Shift+P`
- Type: `Developer: Reload Window`

---

## ⚡ **FASTEST METHOD (If build already done)**

If you just ran `npm run build` and it succeeded:

```powershell
cd cursor-addon
npm run package
cursor --install-extension aimos-cursor-addon.vsix --force
```

Then reload Cursor (`Ctrl+Shift+P` → `Developer: Reload Window`)

---

## 🔍 **WHAT TO CHECK AFTER RELOAD**

1. **Open the Panel:**
   - Command Palette (`Ctrl+Shift+P`) → `AIM-OS: Show Lucid Orchestrator Dashboard`
   - OR: Click the Activity Bar icon → Dashboard

2. **Check if React UI Loads:**
   - ✅ **Success:** You should see tabs (Agents, Chat, Chains, Tools, Timeline, NL Tags)
   - ❌ **Failure:** You'll see fallback HTML with "UI Not Loaded" message

3. **Check Console for Errors:**
   - Right-click in the panel → "Inspect" (or press F12)
   - Check Console tab for any errors
   - Look for `[AIM-OS DEBUG]` messages

---

## 🐛 **IF STILL NOT WORKING**

1. **Check Extension Output:**
   - View → Output
   - Select "AIM-OS Cursor Add-on" from dropdown
   - Look for errors

2. **Check Developer Console:**
   - Right-click panel → Inspect
   - Console tab → Look for red errors

3. **Verify Files Exist:**
   ```powershell
   # Check dist folder exists
   ls cursor-addon/dist/index.html
   ls cursor-addon/dist/assets/
   ```

4. **Try Full Rebuild:**
   ```powershell
   cd cursor-addon
   npm run build  # Rebuilds React UI + Extension
   npm run package
   cursor --install-extension aimos-cursor-addon.vsix --force
   ```

---

## 📝 **SUMMARY**

**You DON'T need to manually uninstall** - the `--force` flag handles it.

**What you DO need:**
1. ✅ Rebuild (already done: `npm run build`)
2. ✅ Package (create .vsix file)
3. ✅ Reinstall with `--force` flag
4. ✅ Reload Cursor window

**Quickest command:**
```powershell
cd cursor-addon && npm run install:windows
```

This does: build → package → install → done! (just reload Cursor)

