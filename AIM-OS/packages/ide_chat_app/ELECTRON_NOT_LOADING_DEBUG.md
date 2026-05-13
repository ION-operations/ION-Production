# Electron App Not Loading - Debugging Guide

**Date:** 2025-11-02  
**Issue:** Standard Electron menu bar visible, but app content not loading. DevTools menu item not working.

---

## 🔍 **DEBUGGING STEPS ADDED**

### **1. Enhanced Logging**
- Added console logs in `main.cjs` for:
  - Build check (dev vs production)
  - Window load events (`did-finish-load`, `dom-ready`, `did-fail-load`)
  - Load URL/file attempts and results
- Added console logs in `main.tsx`:
  - Root element detection
  - App rendering start
- Added console logs in `App.tsx`:
  - Component mount
  - Location/protocol detection

### **2. DevTools Menu Fix**
- Changed `role: 'toggleDevTools'` to explicit `click` handler
- Added `F12` accelerator
- Handler checks if window exists before toggling

### **3. Error Handling**
- Added promise handlers for `loadURL()` and `loadFile()`
- Added fallback UI if root element not found
- Better error logging in main process

---

## 🚨 **IMMEDIATE ACTIONS**

### **Check Electron Console Logs:**
When you launch Electron, check the terminal/console where you ran `npm run electron` for:
- `[Electron] Build check:` - Shows if dev or production mode
- `[Electron] Loading production file:` or `[Electron] Loading dev URL:`
- `[Electron] ✅ Window finished loading` or `[Electron] ❌ Failed to load:`

### **Open DevTools:**
1. **Via Menu:** View → Toggle Developer Tools (should work now)
2. **Via Keyboard:** Press `F12`
3. **Via Shortcut:** `Ctrl+Shift+I` (Windows) or `Cmd+Shift+I` (Mac)

### **Check Console Tab:**
Look for:
- `[main.tsx] ✅ Root element found, rendering App`
- `[App] ✅ Component mounted`
- `[App] Location:` and `[App] Protocol:`
- Any red error messages

---

## 📋 **COMMON ISSUES**

### **Issue 1: Content Not Loading**
**Symptoms:** White/blank screen, menu bar visible  
**Causes:**
- `dist/index.html` doesn't exist or is corrupted
- Build failed silently
- React app crashed during render
- CSP (Content Security Policy) blocking scripts

**Fix:**
1. Check if `dist/index.html` exists: `Test-Path dist\index.html`
2. Rebuild: `npm run build`
3. Check Electron console for load errors
4. Check DevTools Console for React errors

### **Issue 2: DevTools Menu Not Working**
**Symptoms:** Menu item visible but clicking does nothing  
**Causes:**
- `role: 'toggleDevTools'` not working (Electron bug)
- Window not ready when menu clicked

**Fix:** ✅ Changed to explicit `click` handler (already done)

### **Issue 3: React App Not Rendering**
**Symptoms:** Blank screen, no errors in Electron console  
**Causes:**
- Root element not found
- React error during render
- CSS not loading

**Fix:**
1. Check DevTools Console for React errors
2. Check Elements tab for `#root` element
3. Check Network tab for failed CSS/JS loads

---

## 🔧 **NEXT STEPS**

1. **Launch Electron:**
   ```bash
   cd packages/ide_chat_app
   npm run electron
   ```

2. **Check Terminal Output:**
   - Look for `[Electron]` prefixed logs
   - Look for `✅` or `❌` indicators
   - Share any error messages

3. **Open DevTools:**
   - Press `F12` OR
   - View → Toggle Developer Tools

4. **Check DevTools Console:**
   - Look for `[main.tsx]` logs
   - Look for `[App]` logs
   - Look for any red errors

5. **Share Findings:**
   - What do you see in Electron console?
   - What do you see in DevTools Console?
   - Any error messages?

---

## 📊 **EXPECTED BEHAVIOR**

### **Production Build:**
```
[Electron] Build check: { isDev: false, distPath: '...', exists: true }
[Electron] Loading production file: ...\dist\index.html
[Electron] ✅ Production file loaded successfully
[Electron] ✅ Window finished loading
[Electron] ✅ DOM ready
```

### **Development Mode:**
```
[Electron] Build check: { isDev: true, distPath: '...', exists: false }
🚀 Starting Vite dev server...
[Electron] Loading dev URL: http://localhost:3000
[Electron] ✅ Dev URL loaded successfully
[Electron] ✅ Window finished loading
[Electron] ✅ DOM ready
```

### **Renderer Console (DevTools):**
```
[main.tsx] ✅ Root element found, rendering App
[App] ✅ Component mounted
[App] Location: file:///.../dist/index.html
[App] Protocol: file:
```

---

**Status:** 🔴 **DEBUGGING IN PROGRESS**  
**Next:** User checks console logs and DevTools  
**Confidence:** Medium (0.60) - Enhanced logging should reveal issue

