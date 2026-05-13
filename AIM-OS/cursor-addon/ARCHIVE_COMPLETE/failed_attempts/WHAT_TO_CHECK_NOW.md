# 🔍 What to Check Now - After Rebuild

**Extension:** Rebuilt with Sonnet's fixes + Lexicon's diagnostics + Debug command  
**Status:** Installed - Ready to test  
**Date:** 2025-11-01 08:25 AM

---

## ✅ **STEP 1: Run Debug Command**

**How:**
1. Press `Ctrl+Shift+P` (Command Palette)
2. Type: `Debug Dashboard` or `aimos.debugDashboard`
3. Press Enter

**What It Shows:**
- File existence (HTML, assets)
- Script tags found in HTML
- Asset file list
- Instructions for Extension Host console

**This is COPYABLE** - You can copy from Output panel!

---

## ✅ **STEP 2: Check Extension Host Console**

**How:**
1. Help → Toggle Developer Tools
2. Click **"Extension Host"** tab (at top)
3. Look for messages starting with `[DIAGNOSTIC]` or `[AIM-OS]`

**What to Look For:**

### **Critical Messages:**
- `[DIAGNOSTIC] UI PANEL LOADING DIAGNOSTIC START`
- `[DIAGNOSTIC] HTML exists: true/false`
- `[DIAGNOSTIC] Script tags found (BEFORE replacement): X`
- `[DIAGNOSTIC] Script replacements: X of Y replaced`
- `[DIAGNOSTIC] Final script 1 src: vscode-webview://...`
- `[AIM-OS] ✅ TrustedTypes policy created` OR `⚠️ TrustedTypes policy creation failed`

### **If Scripts Don't Convert:**
- `❌ CRITICAL: Script X src NOT a webview URI!`
- `Script replacements: 0 of X replaced`
- → Problem: Regex or file lookup failing

### **If TrustedTypes Fails:**
- `⚠️ TrustedTypes policy creation failed: [error]`
- → Problem: API doesn't exist OR policy name conflict

### **If Everything Works:**
- Scripts converted to `vscode-webview://` ✅
- TrustedTypes policy created ✅
- Dashboard should load!

---

## ✅ **STEP 3: Test Dashboard**

**How:**
1. Click sparkle icon (✨) in Activity Bar
2. OR Press `Ctrl+Shift+P` → type `aim os`

**What Should Happen:**
- **Best Case:** Landing page shows, then dashboard loads
- **Good Case:** Dashboard loads directly
- **Bad Case:** Still blank (but we'll have diagnostic logs!)

---

## 📊 **WHAT DIAGNOSTICS WILL TELL US**

### **Scenario 1: Scripts Don't Convert**
**Signs:**
- `Script replacements: 0 of X replaced`
- `❌ Script src NOT a webview URI!`

**Problem:** Regex not matching OR file lookup failing  
**Fix:** Check regex pattern or file paths

---

### **Scenario 2: TrustedTypes API Doesn't Exist**
**Signs:**
- `⚠️ TrustedTypes policy creation failed`
- No `✅ TrustedTypes policy created` message

**Problem:** `window.trustedTypes` not available in webview  
**Fix:** Non-module build OR different approach

---

### **Scenario 3: CSP Blocking**
**Signs:**
- Scripts converted correctly ✅
- TrustedTypes policy created ✅
- But scripts don't load
- CSP errors in webview console (if accessible)

**Problem:** CSP 'module' directive invalid OR CSP too restrictive  
**Fix:** Remove 'module' from CSP OR adjust CSP policy

---

### **Scenario 4: Everything Works!**
**Signs:**
- Scripts converted to `vscode-webview://` ✅
- TrustedTypes policy created ✅
- Dashboard loads ✅

**Success!** 🎉

---

## 🎯 **PRIORITY CHECKS**

1. **MOST IMPORTANT:** Extension Host console `[DIAGNOSTIC]` messages
2. **SECOND:** Debug command output (copyable!)
3. **THIRD:** Dashboard actually loads or stays blank

---

**After checking, share:**
- Extension Host console messages (all `[DIAGNOSTIC]` and `[AIM-OS]` messages)
- Debug command output
- Whether dashboard loads or stays blank

**This will tell us EXACTLY what's wrong!** 🎯

