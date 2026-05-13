# Cursor Extension Dashboard - Issues Log

**Created:** 2025-11-01  
**Format:** Systematic issue documentation per standards  
**Status:** Comprehensive issue tracking

---

## Issue #1: Packaging Exclusion (.vscodeignore)

**Status:** ✅ FIXED  
**Found By:** Opus  
**Date:** 2025-11-01  
**Attempts:** ~75 before discovery

**Problem:**
- `.vscodeignore` file excluded `dist/` folder from VSIX package
- Extension installed without React UI files
- Showed fallback HTML instead of React UI

**Root Cause:**
- Build process creates `dist/` folder
- `.vscodeignore` had `dist/**` in exclusion list
- VSIX packaging excluded the folder
- Installed extension missing files

**Fix Applied:**
- Modified `.vscodeignore` to include `dist/**`
- Rebuilt VSIX (880KB with 151 files vs 675KB with 47 files)
- Reinstalled extension

**Verification:**
- VSIX size increased ✅
- File count increased ✅
- Files now in package ✅

---

## Issue #2: Missing Activation Events

**Status:** ⚠️ PARTIALLY FIXED  
**Found By:** Lexicon  
**Date:** 2025-11-01  
**Attempts:** ~50 before discovery

**Problem:**
- Extension only activates on commands (`onCommand:aimos.showDashboard`)
- Missing `onView` activation events for webview views
- Extension doesn't activate when panel opens
- `resolveWebviewView` never called → blank screen

**Root Cause:**
- `package.json` `activationEvents` missing `onView:lucidOrchestratorDashboard`
- Missing `onView:aimosDashboard` (if aimos view exists)
- VS Code requires explicit activation events for webview views

**Fix Applied:**
- Added `onView:lucidOrchestratorDashboard` to activationEvents ✅
- `onView:aimosDashboard` still needs verification

**Remaining Work:**
- Verify `views.aimos` exists in package.json
- Add `onView:aimosDashboard` if needed
- Test activation on panel open

---

## Issue #3: Webview Options Order

**Status:** ✅ FIXED  
**Found By:** Aether  
**Date:** 2025-11-01  
**Attempts:** ~40 before discovery

**Problem:**
- Webview options set AFTER HTML assignment
- VS Code requires options BEFORE HTML
- Webview fails to initialize properly
- Causes blank screen

**Root Cause:**
- Code set `webviewView.webview.html = ...` first (line 118)
- Then set `webviewView.webview.options = {...}` (lines 128-134)
- VS Code webview API requires options first

**Fix Applied:**
- Moved options setting BEFORE HTML (lines 100-106) ✅
- Options now set before HTML assignment ✅

**Verification:**
- Code shows correct order ✅
- Options include `enableScripts: true` ✅
- `localResourceRoots` configured ✅

---

## Issue #4: URI Rewriting Complexity

**Status:** ❓ UNKNOWN  
**Found By:** Team analysis  
**Date:** 2025-11-01  
**Attempts:** Multiple fixes attempted

**Problem:**
- HTML has `./assets/main-5fYGI1t7.js` (relative paths)
- Webview needs `vscode-webview://...` URIs
- Regex must match and rewrite all asset paths
- Preserve other attributes (type="module", crossorigin)

**Root Cause:**
- Vite builds with relative paths (`./assets/`)
- VS Code webview requires special URI scheme
- Complex regex matching required
- Edge cases may not be handled

**Fix Attempted:**
- Regex replacement in `getWebviewContent()` method
- Handles both `/assets/` and `./assets/` paths
- Preserves `type="module"` and other attributes
- Cache-busting timestamps added

**Status:**
- Code has regex implementation ✅
- Unknown if regex matches correctly ❓
- Unknown if URIs generated correctly ❓
- Need webview console verification

---

## Issue #5: TrustedTypes Policy

**Status:** ✅ FIXED  
**Found By:** Sonnet  
**Date:** 2025-11-01  
**Attempts:** ~30 before discovery

**Problem:**
- VS Code blocks dynamic scripts without TrustedTypes policy
- Error: "This document requires 'TrustedScript' assignment"
- React scripts fail to load
- Blank screen

**Root Cause:**
- VS Code enforces TrustedTypes security policy
- Scripts injected into webview require policy
- Policy must be created BEFORE CSP meta tag

**Fix Applied:**
- Added TrustedTypes policy creation (lines 352-365) ✅
- Policy created before CSP meta tag ✅
- Allows HTML, Script, ScriptURL creation ✅

**Verification:**
- Code shows policy creation ✅
- Policy created before CSP ✅
- Handles errors gracefully ✅

---

## Issue #6: Content Security Policy (CSP)

**Status:** ✅ FIXED  
**Found By:** Sonnet  
**Date:** 2025-11-01  
**Attempts:** ~30 before discovery

**Problem:**
- CSP blocks module scripts by default
- Error: "no composite descriptor found"
- React scripts fail to load
- Blank screen

**Root Cause:**
- CSP `script-src` didn't include `'module'`
- ES module scripts require explicit permission
- VS Code webview CSP is strict

**Fix Applied:**
- Added `'module'` to `script-src` directive (line 368) ✅
- CSP allows module scripts ✅
- Includes `'unsafe-inline'` and `'unsafe-eval'` ✅

**Verification:**
- Code shows `'module'` in CSP ✅
- CSP allows required script types ✅

---

## Issue #7: React Mounting Failure

**Status:** ❓ UNKNOWN  
**Found By:** Hypothesis  
**Date:** 2025-11-01  
**Attempts:** Not verified

**Problem:**
- React may fail to mount if scripts don't load
- `acquireVsCodeApi()` may fail if extension not activated
- React errors may be hidden
- Blank screen with no errors visible

**Root Cause:**
- Race condition between HTML load and script execution
- Extension context not available when React mounts
- No error handling in React initialization
- Errors hidden in webview console

**Status:**
- Not verified ❓
- Need webview console check ❓
- Need React error handling ❓

---

## Issue #8: Extension Context Timing

**Status:** ❓ UNKNOWN  
**Found By:** Hypothesis  
**Date:** 2025-11-01  
**Attempts:** Not verified

**Problem:**
- `acquireVsCodeApi()` may fail if called before extension activates
- React tries to get VS Code API before it's available
- Communication fails silently
- UI may render but can't communicate

**Root Cause:**
- Timing issue between extension activation and React mounting
- `acquireVsCodeApi()` must be called after extension activates
- No error handling if API unavailable

**Status:**
- Not verified ❓
- Need activation timing verification ❓
- Need error handling ❓

---

## Summary

**Fixed Issues:** 3 (Packaging, Options Order, TrustedTypes/CSP)  
**Partially Fixed:** 1 (Activation Events)  
**Unknown Status:** 3 (URI Rewriting, React Mounting, Extension Context)  
**Total Issues:** 8 critical issues identified

**Next Steps:**
1. Verify activation events complete
2. Check webview console for URI/React errors
3. Test extension context availability
4. Complete systematic debugging

