# Definitive UI Panel Diagnostic Script

**Purpose:** Find the EXACT root cause of UI panel loading failure

---

## 🔍 **STEP-BY-STEP DIAGNOSTIC PROCESS**

### **Step 1: Add Enhanced Logging to Code**

First, we need to add comprehensive logging that will tell us EXACTLY what's happening.

---

### **Step 2: Check Extension Host Console**

1. Open Cursor
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type: `Developer: Toggle Developer Tools`
4. Click on **Console** tab
5. Look for ALL `[AIM-OS DEBUG]` messages

**What to look for:**
- ✅ `[AIM-OS DEBUG] Extension path: [path]` - Verify this is correct
- ✅ `[AIM-OS DEBUG] Looking for HTML at: [path]` - Verify path is correct
- ✅ `[AIM-OS DEBUG] File exists: true/false` - **CRITICAL: Must be `true`**
- ✅ `[AIM-OS DEBUG] ✅ Found React UI HTML! Loading...` - **Must see this**
- ✅ `[AIM-OS DEBUG] ✅ Replacing src: ./assets/main-5fYGI1t7.js -> [webview URI]` - **Must see replacements**
- ✅ `[AIM-OS DEBUG] ✅ Replaced X asset path(s)` - **Must be > 0**
- ❌ `[AIM-OS DEBUG] ❌ Asset not found: [path]` - **If you see this, files missing**
- ❌ `[AIM-OS DEBUG] ❌ dist/index.html not found` - **If you see this, file missing**

**Take screenshot or copy ALL console messages**

---

### **Step 3: Check Webview Console**

1. Right-click inside the panel (where fallback HTML shows)
2. Click **Inspect** (or press `F12`)
3. This opens webview DevTools
4. Click **Console** tab
5. Look for errors

**What to look for:**
- ❌ **404 errors** - `Failed to load resource: vscode-webview://...` - **URIs not accessible**
- ❌ **CSP violations** - `Refused to load script because it violates CSP` - **CSP blocking**
- ❌ **JavaScript errors** - Any red errors - **Script execution failing**
- ❌ **Network tab** - Check if requests are failing (red)

**Take screenshot or copy ALL errors**

---

### **Step 4: Verify Actual HTML Being Served**

1. In webview DevTools (from Step 3)
2. Click **Elements** tab
3. Look at the `<head>` section
4. Find `<script>` and `<link>` tags
5. Check the `src` and `href` attributes

**What to check:**
- Are paths like `vscode-webview://...` (correct) OR `./assets/...` (wrong - not replaced)?
- Are there script tags at all?
- Is `<div id="root">` present?

**Take screenshot of the HTML**

---

### **Step 5: Test Webview URI Access**

Add this to the HTML temporarily to test if webview URIs work:

```javascript
// Add to webview HTML
<script>
  console.log('Webview test script loaded');
  console.log('Webview CSP Source:', document.querySelector('meta[http-equiv="Content-Security-Policy"]'));
</script>
```

---

### **Step 6: Create Diagnostic Test File**

Create a simple test HTML file that will definitively show what's working and what's not.

---

## 🎯 **DEFINITIVE CHECKS**

### **Check 1: File Existence (RUNTIME)**
```typescript
// In lucidDashboardProvider.ts, add:
const distHtmlPath = path.join(this._context.extensionPath, 'dist', 'index.html');
console.log(`[DIAGNOSTIC] Extension path: ${this._context.extensionPath}`);
console.log(`[DIAGNOSTIC] HTML path: ${distHtmlPath}`);
console.log(`[DIAGNOSTIC] HTML exists: ${fs.existsSync(distHtmlPath)}`);
console.log(`[DIAGNOSTIC] HTML readable: ${fs.existsSync(distHtmlPath) ? 'yes' : 'no'}`);
```

### **Check 2: Asset File Existence (RUNTIME)**
```typescript
// After reading HTML, check assets:
const assetFiles = ['main-5fYGI1t7.js', 'main-DftvcEcs.css'];
assetFiles.forEach(file => {
  const assetPath = path.join(this._context.extensionPath, 'dist', 'assets', file);
  console.log(`[DIAGNOSTIC] Asset ${file} exists: ${fs.existsSync(assetPath)}`);
  console.log(`[DIAGNOSTIC] Asset ${file} path: ${assetPath}`);
});
```

### **Check 3: Regex Matching (RUNTIME)**
```typescript
// Test regex before replacement:
const testMatches = htmlContent.match(/(src|href)=["']([^"']*assets\/[^"']+)["']/gi);
console.log(`[DIAGNOSTIC] Regex found ${testMatches ? testMatches.length : 0} matches`);
if (testMatches) {
  testMatches.forEach((match, idx) => {
    console.log(`[DIAGNOSTIC] Match ${idx + 1}: ${match}`);
  });
}
```

### **Check 4: Webview URI Generation (RUNTIME)**
```typescript
// Test URI generation:
const testAssetPath = path.join(this._context.extensionPath, 'dist', 'assets', 'main-5fYGI1t7.js');
const testUri = webview.asWebviewUri(vscode.Uri.file(testAssetPath));
console.log(`[DIAGNOSTIC] Test asset path: ${testAssetPath}`);
console.log(`[DIAGNOSTIC] Test webview URI: ${testUri}`);
console.log(`[DIAGNOSTIC] URI scheme: ${testUri.scheme}`);
console.log(`[DIAGNOSTIC] URI authority: ${testUri.authority}`);
```

### **Check 5: Final HTML Content (RUNTIME)**
```typescript
// After all replacements, log final HTML:
console.log(`[DIAGNOSTIC] Final HTML length: ${htmlContent.length}`);
console.log(`[DIAGNOSTIC] Final HTML has root: ${htmlContent.includes('<div id="root">')}`);
const finalScriptMatches = htmlContent.match(/<script[^>]*src=["']([^"']+)["'][^>]*>/gi);
console.log(`[DIAGNOSTIC] Final HTML script tags: ${finalScriptMatches ? finalScriptMatches.length : 0}`);
if (finalScriptMatches) {
  finalScriptMatches.forEach((script, idx) => {
    console.log(`[DIAGNOSTIC] Final script ${idx + 1}: ${script.substring(0, 150)}`);
  });
}
```

---

## 📋 **DIAGNOSTIC CHECKLIST**

Run through this checklist and note results:

- [ ] **Extension Host Console:**
  - [ ] See "Extension path: [path]" - Path is: ___________
  - [ ] See "HTML exists: true" - YES/NO
  - [ ] See "Found React UI HTML" - YES/NO
  - [ ] See "Replaced X asset path(s)" - Number: ___________
  - [ ] See any "Asset not found" errors - YES/NO (if yes, which files: __________)

- [ ] **Webview Console:**
  - [ ] See 404 errors - YES/NO (if yes, URLs: __________)
  - [ ] See CSP violations - YES/NO (if yes, message: __________)
  - [ ] See JavaScript errors - YES/NO (if yes, error: __________)
  - [ ] Network tab shows failed requests - YES/NO

- [ ] **Webview Elements:**
  - [ ] Script tags have `vscode-webview://` URIs - YES/NO
  - [ ] Script tags still have `./assets/` paths - YES/NO
  - [ ] Root element `<div id="root">` exists - YES/NO

---

## 🎯 **WHAT EACH RESULT MEANS**

### **If HTML exists = false:**
→ **Root Cause:** Extension path wrong OR files not copied correctly
→ **Fix:** Check extension path, verify build script copies files

### **If "Replaced 0 asset path(s)":**
→ **Root Cause:** Regex not matching asset paths
→ **Fix:** Update regex pattern or fix HTML asset path format

### **If "Asset not found" errors:**
→ **Root Cause:** Asset files missing OR wrong filenames
→ **Fix:** Rebuild React UI, verify asset filenames match HTML

### **If webview shows 404 errors:**
→ **Root Cause:** Webview URIs not accessible OR wrong format
→ **Fix:** Check CSP, verify URI generation, check webview permissions

### **If webview shows CSP violations:**
→ **Root Cause:** Content Security Policy blocking scripts
→ **Fix:** Update CSP meta tag, allow webview source

### **If script tags still have `./assets/` paths:**
→ **Root Cause:** Path replacement not working
→ **Fix:** Debug regex matching, verify replacement logic

---

## 🚀 **NEXT STEPS**

1. Add diagnostic logging to code (see below)
2. Rebuild extension
3. Reinstall extension
4. Open panel
5. Run through checklist above
6. Share results

This will give us DEFINITIVE answers, not guesses.

