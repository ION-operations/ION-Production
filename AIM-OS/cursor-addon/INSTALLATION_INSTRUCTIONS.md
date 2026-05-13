# INSTALLATION & TESTING INSTRUCTIONS
**Date:** 2025-11-01  
**Purpose:** Step-by-step guide to test enhanced diagnostics

---

## 🚀 QUICK START

### **Step 1: Build Extension**
```powershell
cd C:\Users\bombe\OneDrive\Desktop\AIM-OS\cursor-addon
npm run compile
npm run package
```

**Note:** TypeScript may show dependency errors (d3-dispatch) - **IGNORE THESE**. They're in node_modules, not our code. Check if `out/extension.js` exists.

---

### **Step 2: Install Extension**
```powershell
code --install-extension aimos-cursor-addon.vsix --force
```

**OR** manually:
1. Open Cursor
2. Extensions view (Ctrl+Shift+X)
3. Click "..." menu → "Install from VSIX..."
4. Select `aimos-cursor-addon.vsix`

---

### **Step 3: Test Diagnostics**

**3A. Check Extension Activation:**
1. Open Cursor 2.0
2. Navigate to: `C:\Users\bombe\.cursor\extensions\aimos.aimos-cursor-addon-1.2.1\`
3. Look for file: `activation-log.txt`
4. **Expected:** File exists with "✅ EXTENSION ACTIVATED" message
5. **If missing:** Extension not activating (fix activation events)

**3B. Check resolveWebviewView() Call:**
1. In Cursor, open **RIGHT SIDEBAR** (where Git/Explorer are)
2. Click **AIM-OS** icon in activity bar (left side)
3. Click **Dashboard** tab
4. Navigate to: `C:\Users\bombe\.cursor\extensions\aimos.aimos-cursor-addon-1.2.1\`
5. Look for file: `resolve-called.txt`
6. **Expected:** File exists with "🎯 RESOLVE FIRED" message
7. **If missing:** `resolveWebviewView()` never called (Cursor 2.0 issue)

**3C. Check Developer Console:**
1. In Cursor, press **F1** → Type "Toggle Developer Tools"
2. Go to **Console** tab
3. Look for messages:
   - `✅✅✅ EXTENSION ACTIVATED ✅✅✅`
   - `🎯🎯🎯 RESOLVE FIRED 🎯🎯🎯`
4. **Expected:** Both messages appear
5. **If only activation:** `resolveWebviewView()` never called

---

## 📊 DECISION TREE

### **Scenario A: activation-log.txt EXISTS, resolve-called.txt EXISTS**
✅ **GOOD NEWS:** Extension activates AND `resolveWebviewView()` IS called!
**Next:** Panel should show content. If blank, issue is HTML/CSP.
**Fix:** Simplify CSP, test with minimal HTML.

---

### **Scenario B: activation-log.txt EXISTS, resolve-called.txt MISSING**
❌ **PROBLEM:** Extension activates but `resolveWebviewView()` NEVER called.
**Root Cause:** Cursor 2.0 not triggering method (platform issue).
**Solutions:**
1. Try `createWebviewPanel` instead (editor area)
2. Try different activation events
3. **Pivot to standalone Electron app** (recommended - faster)

---

### **Scenario C: activation-log.txt MISSING**
❌ **PROBLEM:** Extension not activating at all.
**Fix:** Check activation events in `package.json`, ensure they match view IDs.

---

## 🎯 WHAT TO REPORT

After testing, report:
1. ✅ Does `activation-log.txt` exist? (YES/NO)
2. ✅ Does `resolve-called.txt` exist? (YES/NO)
3. ✅ Does panel show ANY content? (YES/NO - what do you see?)
4. ✅ What messages appear in Developer Console?

---

## ⚡ ALTERNATIVE: Standalone Dashboard

**If extension fails:** We can build standalone Electron app in 1 day.
**Same React UI, same backend, no Cursor extension issues.**

**Would you like me to start on standalone app now?** (Can work in parallel with extension debugging)

---

**Status:** Ready for testing  
**Next:** Install VSIX, test, report results
