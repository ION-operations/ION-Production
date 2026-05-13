# Cursor Extension Dashboard - Troubleshooting Guide

**Created:** 2025-11-01  
**Purpose:** Practical debugging guide for dashboard issues  
**Status:** Complete Troubleshooting Reference

---

## Quick Diagnostic Checklist

### ✅ Step 1: Check Extension Activation

**Symptoms:** Dashboard doesn't open or shows blank

**Diagnosis:**
1. Open Output panel → "AIM-OS Dashboard" channel
2. Look for `[AIM-OS] ✅ resolveWebviewView CALLED`
3. If missing → Extension not activating

**Fix:**
- Check `package.json` activation events:
  ```json
  "activationEvents": [
    "onView:lucidOrchestratorDashboard"
  ]
  ```
- Rebuild and reinstall extension
- Reload Cursor window

---

### ✅ Step 2: Check Build Output

**Symptoms:** Blank dashboard, no errors visible

**Diagnosis:**
1. Check if `cursor-addon/dist/index.html` exists
2. Check if `cursor-addon/dist/assets/` folder exists
3. Check file sizes (should be >100KB for JS files)

**Fix:**
- Run `npm run build` in `cursor-addon/`
- Verify React UI built successfully
- Check `.vscodeignore` includes `!dist/**`
- Rebuild VSIX: `npm run package`

---

### ✅ Step 3: Check Webview Console

**Symptoms:** Dashboard blank, no obvious errors

**How to Access:**
1. Right-click in dashboard panel
2. Select "Inspect" (or "Inspect Element")
3. Open Console tab

**What to Look For:**
- **404 errors:** Asset files not found
  - **Fix:** Check URI rewriting, verify files exist
- **CSP violations:** Content Security Policy blocking
  - **Fix:** Update CSP meta tag, include `'module'` directive
- **TrustedTypes errors:** Policy not created
  - **Fix:** Create TrustedTypes policy before CSP
- **React errors:** Component mounting failures
  - **Fix:** Check React initialization, error boundaries

---

### ✅ Step 4: Check Extension Host Console

**How to Access:**
- VS Code → Help → Toggle Developer Tools
- Console tab shows extension host logs

**What to Look For:**
- `[AIM-OS] ✅ Registered lucidOrchestratorDashboard` → Provider registered
- `[AIM-OS] ✅ resolveWebviewView CALLED` → Webview resolving
- `[DIAGNOSTIC]` messages → Detailed diagnostic information
- Error messages → Specific failure points

---

### ✅ Step 5: Run Debug Command

**Command:** `aimos.debugDashboard`

**What It Does:**
- Checks extension activation status
- Verifies provider registration
- Checks file existence
- Shows comprehensive diagnostics

**How to Use:**
1. Press `Ctrl+Shift+P` (Command Palette)
2. Type "Debug Dashboard"
3. Select "AIM-OS: Debug Dashboard"
4. Check Output panel → "AIM-OS Debug" channel

---

## Common Issues and Solutions

### Issue #1: Blank Dashboard Panel

**Symptoms:**
- Dashboard panel opens but shows blank screen
- No errors visible

**Diagnosis:**
1. Check Extension Host console for `[AIM-OS]` messages
2. Check webview console (right-click → Inspect)
3. Run `aimos.debugDashboard` command

**Common Causes:**
1. **Missing activation events:**
   - `package.json` missing `onView:lucidOrchestratorDashboard`
   - **Fix:** Add to `activationEvents` array

2. **Options set after HTML:**
   - `webviewView.webview.options` set after `webviewView.webview.html`
   - **Fix:** Set options BEFORE HTML in `resolveWebviewView()`

3. **URI rewriting failed:**
   - Asset paths not converted to `vscode-webview://` URIs
   - **Fix:** Check regex replacement in `getWebviewContent()`

4. **TrustedTypes policy missing:**
   - Policy not created before CSP meta tag
   - **Fix:** Create TrustedTypes policy before CSP

5. **CSP blocking scripts:**
   - CSP doesn't include `'module'` directive
   - **Fix:** Update CSP to include `'module'` in `script-src`

**Solution Steps:**
1. Add `onView:lucidOrchestratorDashboard` to `package.json`
2. Set options before HTML in `lucidDashboardProvider.ts`
3. Rebuild and reinstall extension
4. Check webview console for remaining errors

---

### Issue #2: 404 Errors for Assets

**Symptoms:**
- Webview console shows 404 errors for JS/CSS files
- Dashboard blank or partially loaded

**Diagnosis:**
1. Check webview console (right-click → Inspect → Console)
2. Look for 404 errors with asset filenames
3. Check if URIs are `vscode-webview://` scheme

**Common Causes:**
1. **Files not in VSIX:**
   - `.vscodeignore` excludes `dist/` folder
   - **Fix:** Add `!dist/**` to `.vscodeignore`

2. **Files not built:**
   - React UI not built before packaging
   - **Fix:** Run `npm run build` before `npm run package`

3. **URI rewriting failed:**
   - Regex doesn't match asset paths
   - **Fix:** Check regex in `getWebviewContent()`, verify file existence

4. **Wrong file paths:**
   - Asset paths don't match actual files
   - **Fix:** Check build output, verify file names

**Solution Steps:**
1. Check `.vscodeignore` includes `!dist/**`
2. Run `npm run build` to rebuild React UI
3. Check `dist/assets/` folder exists with files
4. Rebuild VSIX: `npm run package`
5. Reinstall extension
6. Check webview console for URI format

---

### Issue #3: CSP Violations

**Symptoms:**
- Webview console shows CSP violation errors
- Scripts blocked by Content Security Policy

**Diagnosis:**
1. Check webview console for CSP violation messages
2. Look for "Refused to execute inline script" or similar
3. Check CSP meta tag in generated HTML

**Common Causes:**
1. **Missing 'module' directive:**
   - CSP `script-src` doesn't include `'module'`
   - **Fix:** Add `'module'` to `script-src` directive

2. **Missing 'unsafe-inline':**
   - CSP blocks inline scripts (React needs this)
   - **Fix:** Include `'unsafe-inline'` in `script-src`

3. **Wrong URI scheme:**
   - CSP doesn't allow `vscode-webview:` scheme
   - **Fix:** Include `vscode-webview:` in CSP directives

**Solution Steps:**
1. Update CSP in `getWebviewContent()`:
   ```typescript
   "script-src 'unsafe-inline' 'unsafe-eval' 'module' vscode-webview:;"
   ```
2. Rebuild and reinstall extension
3. Check webview console for remaining violations

---

### Issue #4: TrustedTypes Errors

**Symptoms:**
- Webview console shows "This document requires 'TrustedScript' assignment"
- Scripts fail to load

**Diagnosis:**
1. Check webview console for TrustedTypes errors
2. Check if TrustedTypes policy script exists in HTML
3. Verify policy created before CSP meta tag

**Common Causes:**
1. **Policy not created:**
   - TrustedTypes policy script missing
   - **Fix:** Create policy in `getWebviewContent()`

2. **Policy created after CSP:**
   - CSP meta tag before TrustedTypes script
   - **Fix:** Inject TrustedTypes script BEFORE CSP meta tag

3. **Policy creation failed:**
   - Error in policy creation code
   - **Fix:** Check error handling, verify browser support

**Solution Steps:**
1. Create TrustedTypes policy in `getWebviewContent()`:
   ```typescript
   const trustedTypesScript = `
   <script>
   (function() {
       if (typeof window.trustedTypes !== 'undefined') {
           window.trustedTypes.createPolicy('aimos-policy', {
               createHTML: (html) => html,
               createScript: (script) => script,
               createScriptURL: (url) => url
           });
       }
   })();
   </script>`;
   ```
2. Inject BEFORE CSP meta tag:
   ```typescript
   htmlContent = htmlContent.replace('<head>', `<head>\n${trustedTypesScript}`);
   ```
3. Rebuild and reinstall extension
4. Check webview console for TrustedTypes messages

---

### Issue #5: React Not Mounting

**Symptoms:**
- HTML loads but React UI doesn't appear
- No React components visible

**Diagnosis:**
1. Check webview console for React errors
2. Check if `acquireVsCodeApi()` is called
3. Check if scripts loaded successfully
4. Check if root element exists in HTML

**Common Causes:**
1. **Scripts not loading:**
   - 404 errors, CSP violations, TrustedTypes errors
   - **Fix:** Fix script loading issues first

2. **acquireVsCodeApi() fails:**
   - VS Code API not available
   - **Fix:** Check webview context, handle errors

3. **Root element missing:**
   - HTML doesn't have `<div id="root">`
   - **Fix:** Verify React build output includes root element

4. **React error boundary:**
   - Component error caught by error boundary
   - **Fix:** Check error boundary for error messages

**Solution Steps:**
1. Fix script loading issues (404, CSP, TrustedTypes)
2. Check React initialization code
3. Verify root element exists: `<div id="root"></div>`
4. Check error boundaries for component errors
5. Check webview console for React error messages

---

## Diagnostic Commands

### Command: `aimos.debugDashboard`

**Purpose:** Comprehensive diagnostic information

**Output:**
- Extension activation status
- Provider registration status
- File existence checks
- Path verification
- Forced reveal attempt

**How to Use:**
1. Press `Ctrl+Shift+P`
2. Type "Debug Dashboard"
3. Select "AIM-OS: Debug Dashboard"
4. Check Output panel → "AIM-OS Debug" channel

---

## File Verification Checklist

### ✅ Pre-Build Verification

- [ ] `package.json` has correct activation events
- [ ] `package.json` has correct view registration
- [ ] `.vscodeignore` includes `!dist/**`
- [ ] `tsconfig.json` configured correctly

### ✅ Build Verification

- [ ] React UI builds successfully (`npm run build` in `packages/ide_chat_app/`)
- [ ] `cursor-addon/dist/index.html` exists
- [ ] `cursor-addon/dist/assets/` folder exists
- [ ] Asset files have reasonable sizes (>100KB for JS)

### ✅ Packaging Verification

- [ ] VSIX builds successfully (`npm run package`)
- [ ] VSIX size reasonable (~880KB with React UI)
- [ ] VSIX contains `dist/` folder
- [ ] VSIX contains `out/extension.js`

### ✅ Installation Verification

- [ ] Extension installs without errors
- [ ] Extension appears in Extensions list
- [ ] Dashboard panel icon appears
- [ ] Extension activates on panel open

### ✅ Runtime Verification

- [ ] Extension Host console shows activation logs
- [ ] Output panel shows `[AIM-OS]` messages
- [ ] Webview console accessible (right-click → Inspect)
- [ ] Dashboard panel opens without errors

---

## Emergency Recovery Procedures

### Complete Reset

**If nothing works, try complete reset:**

1. **Uninstall Extension:**
   - VS Code → Extensions → AIM-OS → Uninstall
   - Or: `code --uninstall-extension aimos.aimos-cursor-addon`

2. **Clean Build:**
   ```bash
   cd cursor-addon
   rm -rf dist/ out/ node_modules/
   npm install
   npm run build
   npm run package
   ```

3. **Reinstall:**
   ```bash
   code --install-extension aimos-cursor-addon.vsix --force
   ```

4. **Reload Cursor:**
   - Press `Ctrl+Shift+P` → "Reload Window"

---

## Getting Help

### Diagnostic Information to Collect

1. **Extension Host Console:**
   - Copy all `[AIM-OS]` messages
   - Copy any error messages

2. **Webview Console:**
   - Right-click dashboard → Inspect → Console
   - Copy all errors and warnings

3. **Output Channels:**
   - "AIM-OS Dashboard" channel contents
   - "AIM-OS Debug" channel contents (if run)

4. **File Verification:**
   - Check if `dist/index.html` exists
   - Check if `dist/assets/` folder exists
   - Check VSIX file size

5. **Configuration:**
   - `package.json` activation events
   - `.vscodeignore` contents
   - Extension version

---

## Summary

This troubleshooting guide provides step-by-step procedures for diagnosing and fixing common dashboard issues. Follow the diagnostic checklist, check common issues, verify files, and use emergency recovery procedures if needed. Collect diagnostic information before seeking help.


