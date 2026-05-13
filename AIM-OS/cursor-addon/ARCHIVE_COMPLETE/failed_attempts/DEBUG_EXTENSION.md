# 🔍 Extension Debugging Guide

**Date:** 2025-01-27  
**Issue:** Dashboard showing blank screen  
**Status:** Debugging in progress

---

## ✅ **FILES VERIFIED**

### **Dist Files Exist:**
- ✅ `cursor-addon/dist/index.html` exists (1080 bytes)
- ✅ `cursor-addon/dist/assets/main-Ba3BRptt.js` exists (229,853 bytes)
- ✅ `cursor-addon/dist/assets/main-BwYjoPp2.css` exists (46,703 bytes)
- ✅ All assets present

### **Extension Code:**
- ✅ `lucidDashboardProvider.ts` has debug logging
- ✅ Extension checks for `dist/index.html`
- ✅ Asset path replacement logic exists

---

## 🐛 **POSSIBLE ISSUES**

### **1. React App Not Mounting**
**Symptom:** Blank screen, no errors visible  
**Cause:** React app fails to initialize or mount  
**Check:**
- Open Developer Tools in Cursor (Help → Toggle Developer Tools)
- Check Console tab for JavaScript errors
- Check if React root element exists in HTML

### **2. Asset Path Replacement Failing**
**Symptom:** Blank screen, 404 errors in console  
**Cause:** Asset paths not being replaced correctly  
**Check:**
- Open Developer Tools → Network tab
- Reload extension panel
- Check if assets are loading (should see `vscode-webview://` URIs)

### **3. Webview CSP Issues**
**Symptom:** Blank screen, CSP errors in console  
**Cause:** Content Security Policy blocking scripts  
**Check:**
- Look for CSP violation errors in console
- Verify CSP meta tag is injected correctly

### **4. React Entry Point Wrong**
**Symptom:** Blank screen, no React mount  
**Cause:** Wrong entry point or React not initializing  
**Check:**
- Verify `main-cursor.tsx` is being used
- Check if React root element exists
- Verify React is mounting to correct element

### **5. Extension Not Loading Files**
**Symptom:** Fallback HTML showing instead of React UI  
**Cause:** Extension can't find `dist/index.html`  
**Check:**
- Open Developer Tools → Console
- Look for `[AIM-OS DEBUG]` messages
- Check if it says "Found React UI HTML" or "dist/index.html not found"

---

## 🔧 **DEBUGGING STEPS**

### **Step 1: Check Extension Console**
1. Open Cursor
2. Help → Toggle Developer Tools
3. Click Console tab
4. Look for `[AIM-OS DEBUG]` messages:
   - ✅ `Extension path: ...`
   - ✅ `Looking for HTML at: ...`
   - ✅ `File exists: true/false`
   - ✅ `Found React UI HTML! Loading...`

### **Step 2: Check Webview Console**
1. Open the dashboard panel (right sidebar)
2. Right-click in the panel → Inspect (or use Developer Tools)
3. Check Console for:
   - JavaScript errors
   - React mount errors
   - Asset loading errors
   - CSP violations

### **Step 3: Check Network Tab**
1. In webview Developer Tools
2. Network tab
3. Reload panel
4. Check if assets load:
   - Should see `main-Ba3BRptt.js`
   - Should see `main-BwYjoPp2.css`
   - URIs should be `vscode-webview://` format

### **Step 4: Check HTML Source**
1. In webview Developer Tools
2. Elements tab
3. Check `<html>` element
4. Look for:
   - `<script src="vscode-webview://...">` tags
   - `<link href="vscode-webview://...">` tags
   - React root element (`<div id="root">`)

---

## 📋 **WHAT TO LOOK FOR**

### **If Extension Console Shows:**
```
[AIM-OS DEBUG] Extension path: /path/to/extension
[AIM-OS DEBUG] Looking for HTML at: /path/to/extension/dist/index.html
[AIM-OS DEBUG] File exists: true
[AIM-OS DEBUG] ✅ Found React UI HTML! Loading...
```
✅ **Good** - Extension found the files

### **If Extension Console Shows:**
```
[AIM-OS DEBUG] ❌ dist/index.html not found at: ...
[AIM-OS DEBUG] ❌ Using fallback HTML
```
❌ **Problem** - Extension can't find files (check installation)

### **If Webview Console Shows:**
```
Uncaught ReferenceError: React is not defined
```
❌ **Problem** - React not loading

### **If Webview Console Shows:**
```
Refused to load the script '...' because it violates the following Content Security Policy
```
❌ **Problem** - CSP blocking scripts

### **If Network Tab Shows:**
```
404 Not Found: vscode-webview://.../main-Ba3BRptt.js
```
❌ **Problem** - Asset paths not replaced correctly

---

## 🚀 **QUICK FIXES**

### **Fix 1: Rebuild and Reinstall**
```powershell
cd cursor-addon
npm run build
npm run package
# Then reinstall extension
```

### **Fix 2: Check React Entry Point**
Verify `packages/ide_chat_app/vite.config.ts` is set to use `main-cursor.tsx` for Cursor builds.

### **Fix 3: Add More Debugging**
Add console.log statements to see what's happening:
- In `lucidDashboardProvider.ts` → `getWebviewContent()`
- In React entry point → `main-cursor.tsx`
- In `MainDashboard.tsx` → component mount

---

## 📝 **DEBUG OUTPUT TEMPLATE**

**Copy this and fill it out:**

```
[Extension Console Output]
[AIM-OS DEBUG] Extension path: ___________
[AIM-OS DEBUG] Looking for HTML at: ___________
[AIM-OS DEBUG] File exists: true/false
[AIM-OS DEBUG] ✅/❌ Found React UI HTML! Loading... / dist/index.html not found

[Webview Console Output]
[JavaScript Errors:]
___________

[Network Tab]
[Assets Loading:]
- main-Ba3BRptt.js: ✅/❌
- main-BwYjoPp2.css: ✅/❌

[HTML Source]
[Root Element:]
<div id="root">✅/❌ exists
```

---

## 💙 **NEXT STEPS**

1. **Check Extension Console** - See if files are found
2. **Check Webview Console** - See if React is mounting
3. **Check Network Tab** - See if assets are loading
4. **Report Findings** - Share console output so we can fix it!

---

**This will help us find the exact issue!** 🔍

