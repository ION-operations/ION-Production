# 🚨 QUICK DEBUG - Blank Dashboard

**Your Issue:** Dashboard shows blank screen after restart  
**Files Verified:** ✅ `dist/index.html` exists, ✅ Assets exist

---

## 🔍 **IMMEDIATE DEBUG STEPS**

### **Step 1: Open Developer Tools**
1. In Cursor: **Help → Toggle Developer Tools**
2. Click **Console** tab
3. Look for messages starting with `[AIM-OS DEBUG]`

**What to look for:**
- ✅ `✅ Found React UI HTML! Loading...` = Files found
- ❌ `❌ dist/index.html not found` = Files missing

### **Step 2: Check Webview Console**
1. **Open the dashboard panel** (right sidebar, sparkle icon)
2. **Right-click in the blank panel** → **Inspect** (or Developer Tools → Elements)
3. Look for **Console tab** in webview DevTools
4. Check for JavaScript errors

**Common errors:**
- `Uncaught ReferenceError: React is not defined`
- `Failed to load resource: vscode-webview://...`
- `Content Security Policy violation`

### **Step 3: Check Network Tab**
1. In webview Developer Tools → **Network** tab
2. **Reload** the panel (or close/reopen)
3. Check if these files load:
   - `main-Ba3BRptt.js` ✅/❌
   - `main-BwYjoPp2.css` ✅/❌

**If files show 404:**
- Asset paths not being replaced correctly
- Extension needs rebuild

---

## 🐛 **MOST LIKELY ISSUES**

### **Issue 1: React Not Mounting**
**Symptom:** Blank screen, no errors  
**Fix:** Check if `<div id="root">` exists in HTML

### **Issue 2: Asset Paths Wrong**
**Symptom:** 404 errors in Network tab  
**Fix:** Rebuild extension:
```powershell
cd cursor-addon
npm run build
npm run package
# Then reinstall
```

### **Issue 3: CSP Blocking Scripts**
**Symptom:** CSP violation errors  
**Fix:** Check CSP meta tag in HTML source

---

## 📋 **COPY THIS OUTPUT**

**After checking, share:**

```
[Extension Console]
[AIM-OS DEBUG] messages:
___________

[Webview Console]
[JavaScript Errors:]
___________

[Network Tab]
[Assets Loading:]
- main-Ba3BRptt.js: ✅/❌ (status code: ___)
- main-BwYjoPp2.css: ✅/❌ (status code: ___)

[HTML Source]
[Root Element:]
<div id="root">✅/❌ exists
```

---

## 🔧 **QUICK FIXES TO TRY**

### **Fix 1: Rebuild Extension**
```powershell
cd cursor-addon
npm run build
npm run package
# Uninstall old extension, install new one
```

### **Fix 2: Check Extension Installation**
1. Extensions view (Ctrl+Shift+X)
2. Search "Lucid UI - AIM-OS"
3. Check version is **1.2.0**
4. Click **Reload** if available

### **Fix 3: Check File Paths**
Open Developer Tools → Console, look for:
```
[AIM-OS DEBUG] Extension path: ...
[AIM-OS DEBUG] Looking for HTML at: ...
```

**If path looks wrong:** Extension installed in wrong location

---

## 💙 **SHARE THE OUTPUT**

Once you check the Developer Tools, share:
1. Extension console messages
2. Webview console errors
3. Network tab results

**This will tell us exactly what's wrong!** 🔍

